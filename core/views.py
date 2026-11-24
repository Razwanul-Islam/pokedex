from rest_framework.generics import GenericAPIView
from django.views.generic import TemplateView, ListView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import google.generativeai as genai
from django.conf import settings
from PIL import Image
import json
from .models import CollectionEntry

genai.configure(api_key=settings.GEMENI_API_KEY)

# Index page
class HomeView(TemplateView):
    template_name = "index.html"


class CollectionView(ListView):
    model = CollectionEntry
    template_name = 'collection.html'
    context_object_name = 'entries'

# generate info
class generate_info(GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]

    # get image file from request and process it with gemini api
    def post(self, request):
        image_DATA = request.FILES.get('image')
        if not image_DATA:
            return Response({'error': 'An image is required.'}, status=400)
        # MAKE IMAGE FILE FROM request.FILES['image'] WITH Image of Pillow
        try:
            image = Image.open(image_DATA)
            image.load()
        except (OSError, ValueError):
            return Response({'error': 'Please upload a valid image.'}, status=400)
        # write reqruired prompt
        prompt = "You are a pokedex. A image will be giving to you (that might be a pokemon or real life thing) if the image is about pokemon then give info about pokemon in json formate, or the image is real life thing then give info of that thing if that is a pokemon make sure to give pokemon type based on their real life livlihood (but use description more pokemon like). Must add parameter name, description, type, abilities, weaknesses, strengths, evolution, region, habitat, rareness, common moves, special moves"
        # initialize gemini model
        model = genai.GenerativeModel("gemini-1.5-flash")
        # generate content from image and prompt
        response = model.generate_content([prompt, image])
        # process response and return it
        # first get position of first { and last } in response
        start = response.text.find("{")
        end = response.text.rfind("}")
        # extract json from response
        response = response.text[start:end+1]
        # replace \n with " " in response
        response = response.replace("\n", " ")
        # convert response to json
        response = json.loads(response)
        if not isinstance(response, dict):
            return Response({'error': 'The generated entry was invalid.'}, status=502)
        image_DATA.seek(0)
        entry = CollectionEntry(result=response)
        try:
            entry.image.save(image_DATA.name, image_DATA, save=False)
            entry.save()
        except Exception:
            if entry.image.name:
                entry.image.delete(save=False)
            raise
        # give response
        return Response(response)
