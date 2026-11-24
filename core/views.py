from rest_framework.generics import GenericAPIView
from django.views.generic import TemplateView, ListView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import google.generativeai as genai
from django.conf import settings
from PIL import Image
import json
from .models import Battle, CollectionEntry
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from uuid import uuid4

genai.configure(api_key=settings.GEMENI_API_KEY)

# Index page
class HomeView(TemplateView):
    template_name = "index.html"


class CollectionView(ListView):
    model = CollectionEntry
    template_name = 'collection.html'
    context_object_name = 'entries'


def battle(request):
    current = Battle.objects.filter(session_key=request.session.session_key).first() if request.session.session_key else None
    return render(request, 'battle.html', {
        'entries': CollectionEntry.objects.all(),
        'battle': current.state if current else None,
    })


@require_POST
def battle_start(request):
    entry_id = request.POST.get('entry', '')
    if not entry_id.isascii() or not entry_id.isdigit() or len(entry_id) > 18:
        return HttpResponseBadRequest('Choose an available collection entry.')
    entry = CollectionEntry.objects.filter(pk=int(entry_id)).first()
    if entry is None:
        return HttpResponseBadRequest('Choose an available collection entry.')
    result = entry.result if isinstance(entry.result, dict) else {}
    name = result.get('name')
    if not isinstance(name, str) or not name.strip():
        name = 'Unidentified specimen'
    if not request.session.session_key:
        request.session.create()
    token = uuid4().hex
    state = {
        'player': name[:100], 'opponent': 'Pikachu',
        'player_hp': 100, 'opponent_hp': 100, 'status': 'active',
        'events': [f'{name[:100]} enters the battle against Pikachu!'],
        'turn_token': token,
    }
    Battle.objects.update_or_create(session_key=request.session.session_key, defaults={'turn_token': token, 'state': state})
    return redirect('battle')


@require_POST
def battle_turn(request):
    token = request.POST.get('turn_token')
    current = Battle.objects.filter(session_key=request.session.session_key, turn_token=token).first() if request.session.session_key and token else None
    state = current.state if current else None
    if (not state or state.get('status') != 'active'
            or request.POST.get('action') not in ('attack', 'quick')
            or request.POST.get('turn_token') != state.get('turn_token')):
        return HttpResponseBadRequest('Invalid battle action or battle is over.')

    player_damage = 25 if request.POST['action'] == 'attack' else 15
    state['opponent_hp'] = max(0, state['opponent_hp'] - player_damage)
    events = [f"{state['player']} attacks Pikachu for {player_damage} damage."]
    if state['opponent_hp'] == 0:
        state['status'] = 'won'
        events.append('Pikachu fainted. You win!')
    else:
        # The opponent uses a stronger attack when its health is low.
        damage = 35 if state['opponent_hp'] <= 50 else 20
        state['player_hp'] = max(0, state['player_hp'] - damage)
        events.append(f'Pikachu attacks {state["player"]} for {damage} damage.')
        if state['player_hp'] == 0:
            state['status'] = 'lost'
            events.append(f'{state["player"]} fainted. You lose!')
    state['events'] = events
    state['turn_token'] = uuid4().hex
    # The token comparison and state write must be one database operation. A
    # competing turn or a new battle invalidates this snapshot before it saves.
    updated = Battle.objects.filter(pk=current.pk, turn_token=token).update(
        turn_token=state['turn_token'], state=state,
    )
    if not updated:
        return HttpResponseBadRequest('Invalid battle action or battle is over.')
    return redirect('battle')

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
