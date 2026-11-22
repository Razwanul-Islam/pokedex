from django.test import TestCase


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
