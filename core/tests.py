import io
import json
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import Battle, CollectionEntry


class HomeViewTests(TestCase):
    def test_home_page_includes_the_scanner_upload_and_result_targets(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'href="/static/css/pokedex.css"')
        self.assertContains(response, 'id="upload-area"')
        self.assertContains(response, 'id="file-input"')
        self.assertContains(response, 'id="result-content" hidden')
        self.assertContains(response, 'id="scan-another"')
        self.assertContains(response, "fetch('generate-info/'")

    def test_home_page_formats_string_list_or_object_list_evolution_values(self):
        response = self.client.get('/')

        self.assertContains(response, "function listValue(value)")
        self.assertContains(response, "function evolutionValue(value)")
        self.assertContains(response, "evolution.name || evolution.species || evolution.pokemon || evolution.to")
        self.assertContains(response, "setEntry('pokemon-evolution', evolutionValue(data.evolution) || 'None');")
        self.assertContains(response, "scanAnother.addEventListener('click'")
        self.assertContains(response, "fileInput.value = '';")

    def test_home_page_clears_the_selected_file_after_a_failed_request(self):
        response = self.client.get('/')

        self.assertContains(response, "pokemonImage.style.display = 'none';\n            fileInput.value = '';\n            alert('An error occurred while processing the image.');")

    def test_home_page_ignores_stale_scan_callbacks(self):
        response = self.client.get('/')

        self.assertContains(response, 'let scanGeneration = 0;')
        self.assertContains(response, 'const generation = ++scanGeneration;')
        self.assertContains(response, 'if (generation !== scanGeneration) return;')
        self.assertContains(response, 'scanGeneration += 1;')


class CollectionTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.media.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    @patch('core.views.genai.GenerativeModel')
    def test_scan_saves_result_and_original_image_for_collection(self, model):
        data = {'name': 'Pikachu', 'description': 'A discovery', 'abilities': ['Static']}
        model.return_value.generate_content.return_value.text = json.dumps(data)
        image = io.BytesIO()
        Image.new('RGB', (2, 2), 'yellow').save(image, format='PNG')
        image_bytes = image.getvalue()

        response = self.client.post('/generate-info/', {
            'image': SimpleUploadedFile('specimen.png', image_bytes, content_type='image/png'),
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), data)
        entry = CollectionEntry.objects.get()
        self.assertEqual(entry.result, data)
        with entry.image.open('rb') as saved_image:
            self.assertEqual(saved_image.read(), image_bytes)
        for _ in range(2):
            book = self.client.get('/collection/')
            self.assertContains(book, 'Pikachu')
            self.assertContains(book, 'A discovery')
            self.assertContains(book, entry.image.url)
        # Exercise Django's development media serving with the temporary media root.
        from django.views.static import serve
        from django.test import RequestFactory
        served = serve(RequestFactory().get(entry.image.url), entry.image.name, document_root=self.media.name)
        self.assertEqual(b''.join(served.streaming_content), image_bytes)
        served.close()

    @patch('core.views.genai.GenerativeModel')
    def test_invalid_upload_does_not_create_entry(self, model):
        response = self.client.post('/generate-info/', {
            'image': SimpleUploadedFile('bad.png', b'not an image', content_type='image/png'),
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CollectionEntry.objects.exists())
        model.assert_not_called()

    def test_empty_collection(self):
        self.assertContains(self.client.get('/collection/'), 'No saved scans yet.')


class BattleTests(TestCase):
    def setUp(self):
        self.entry = CollectionEntry.objects.create(image='collection/test.png', result={'name': 'Bulbasaur'})

    def start(self):
        return self.client.post('/battle/start/', {'entry': self.entry.pk})

    def state(self):
        return Battle.objects.get(session_key=self.client.session.session_key).state

    def turn(self, action='attack'):
        return self.client.post('/battle/turn/', {
            'action': action, 'turn_token': self.state()['turn_token'],
        })

    def test_setup_and_session_isolation(self):
        from django.test import Client
        self.assertContains(self.client.get('/battle/'), 'Bulbasaur')
        self.assertEqual(self.start().status_code, 302)
        response = self.client.get('/battle/')
        self.assertContains(response, 'Your Pokémon: Bulbasaur')
        self.assertContains(response, 'Computer: Pikachu')
        self.assertContains(response, 'Health: 100 / 100', count=2)
        self.assertNotContains(Client().get('/battle/'), 'Battle status')

    def test_turn_and_stale_token(self):
        self.start()
        token = self.state()['turn_token']
        self.assertEqual(self.turn().status_code, 302)
        state = self.state()
        self.assertEqual((state['player_hp'], state['opponent_hp']), (80, 75))
        self.assertContains(self.client.get('/battle/'), 'Pikachu attacks Bulbasaur for 20 damage.')
        self.assertEqual(self.client.post('/battle/turn/', {'action': 'attack', 'turn_token': token}).status_code, 400)
        self.assertEqual(self.state(), state)

    def test_overlapping_turns_consume_token_once(self):
        from django.test import Client
        from uuid import uuid4

        self.start()
        token = self.state()['turn_token']
        other = Client()
        other.cookies.update(self.client.cookies)
        competing_responses = []

        def interleaved_uuid():
            # The first request has read its state; complete a second request
            # before allowing the first to perform its conditional update.
            if not competing_responses:
                competing_responses.append(None)
                competing_responses[0] = other.post('/battle/turn/', {
                    'action': 'quick', 'turn_token': token,
                })
            return uuid4()

        with patch('core.views.uuid4', side_effect=interleaved_uuid):
            response = self.client.post('/battle/turn/', {'action': 'attack', 'turn_token': token})

        self.assertEqual(competing_responses[0].status_code, 302)
        self.assertEqual(response.status_code, 400)
        state = self.state()
        self.assertEqual((state['player_hp'], state['opponent_hp']), (80, 85))
        self.assertNotEqual(state['turn_token'], token)

    def test_invalid_requests(self):
        self.assertEqual(self.client.post('/battle/turn/', {'action': 'attack'}).status_code, 400)
        for entry in ('', '-1', 'abc', '9' * 100, '999999'):
            self.assertEqual(self.client.post('/battle/start/', {'entry': entry}).status_code, 400)
        self.assertEqual(self.client.get('/battle/start/').status_code, 405)
        self.assertEqual(self.client.get('/battle/turn/').status_code, 405)
        self.start()
        state = self.state()
        self.assertEqual(self.turn('invalid').status_code, 400)
        self.assertEqual(self.state(), state)

    def test_victory_and_new_battle(self):
        self.start()
        for _ in range(4):
            self.turn()
        state = self.state()
        self.assertEqual((state['status'], state['player_hp'], state['opponent_hp']), ('won', 10, 0))
        self.assertContains(self.client.get('/battle/'), 'Victory! You win.')
        self.assertEqual(self.turn().status_code, 400)
        self.start()
        self.assertEqual(self.state()['status'], 'active')
        self.assertEqual(self.state()['player_hp'], 100)
        self.assertNotEqual(self.state()['turn_token'], state['turn_token'])

    def test_defeat(self):
        self.start()
        for _ in range(5):
            self.turn('quick')
        state = self.state()
        self.assertEqual((state['status'], state['player_hp']), ('lost', 0))
        self.assertContains(self.client.get('/battle/'), 'Defeat. You lose.')
        self.assertEqual(self.turn().status_code, 400)

    def test_empty_collection(self):
        self.entry.delete()
        self.assertContains(self.client.get('/battle/'), 'No saved scans yet.')
