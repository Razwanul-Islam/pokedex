import io
import json
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import CollectionEntry


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
