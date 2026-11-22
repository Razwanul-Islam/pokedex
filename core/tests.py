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
        self.assertContains(response, "fetch('generate-info/'")
