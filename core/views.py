from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import google.generativeai as genai
from django.conf import settings
from PIL import Image
import json

genai.configure(api_key=settings.GEMENI_API_KEY)

# Index page
class HomeView(TemplateView):
    template_name = "index.html"

# generate info
class generate_info(GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]

    # get image file from request and process it with gemini api
    def post(self, request):
        image_DATA = request.FILES['image']
        # MAKE IMAGE FILE FROM request.FILES['image'] WITH Image of Pillow
        image = Image.open(image_DATA)
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
        # give response
        return Response(response)