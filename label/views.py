import numpy as np
import os
from django.shortcuts import render
from django.http import HttpResponse
import json
from .models import Dataset, Box
from collections import Counter
import glob
from skimage import io

BOX_SIZE = 100
PADDING = 50

static_dir = os.path.join(os.path.dirname(__file__), 'static/')
folders = [x[0].split('/')[-1] for x in os.walk(static_dir)][1:]
minus = {}
plus = {}
for fold in folders:
    pattern = os.path.join(static_dir, fold, '*_-*.png')
    minus[fold] = len(glob.glob(pattern))
    pattern = os.path.join(static_dir, fold, '*_+*.png')
    plus[fold] = len(glob.glob(pattern))


def index(request):
    r = request.GET

    if 'name' in r:
        folder = r['name']
    else:
        folder = _choose_folder()
    img = io.imread(os.path.join(static_dir, folder, 'w.png'))

    try:
        dataset = Dataset.objects.get(name=folder)
        data = dataset.data
    except Dataset.DoesNotExist:
        data = '{}'
        dataset = None

    h, w = img.shape[:2]
    if 'x0' in r:
        box = [r['x0'], r['y0'], r['size']]
    else:
        box = _retry_gen_box(dataset, h, w)

    box_saved = False
    if dataset is not None:
        try:
            Box.objects.get(x0=box[0], y0=box[1], size=box[2], dataset=dataset)
            box_saved = True
        except Box.DoesNotExist:
            pass

    ddata = json.loads(data)
    index = max(map(int, ddata)) + 1 if len(ddata) else 0
    context = {'name': folder, 'data': data, 'index': index,
               'plus': plus[folder], 'minus': minus[folder],
               'box': box, 'h': h, 'w': w, 'box_saved': box_saved}
    return render(request, "main.html", context)


def _retry_gen_box(dataset, h, w):
    box = _gen_box(w, h)
    if dataset is not None:
        tries = 10
        boxes = Box.objects.filter(dataset=dataset)
        for _ in range(tries):
            box = _gen_box(w, h)
            closest = 1000
            for old_box in boxes:
                dist_x = abs(old_box.x0 - box[0]) / box[2]
                dist_y = abs(old_box.y0 - box[1]) / box[2]
                dist = dist_x + dist_y
                if dist < closest:
                    closest = dist
            if closest > 2:
                break
    return box


def _gen_box(w, h):
    x0 = np.random.randint(PADDING, w - PADDING - BOX_SIZE)
    y0 = np.random.randint(PADDING, h - PADDING - BOX_SIZE)
    return [x0, y0, BOX_SIZE]


def _choose_folder():
    c = Counter()
    for folder in folders:
        try:
            data = Dataset.objects.get(name=folder).data
            c[folder] = len(json.loads(data))
        except Dataset.DoesNotExist:
            pass
    # p = np.array([1 / (1 + c[folder]) for folder in folders])
    p = np.array([1.0 for folder in folders])
    p /= p.sum()
    folder = np.random.choice(folders, p=p)
    return folder


def save(request):
    data = json.loads(request.body)
    try:
        obj = Dataset.objects.get(name=data['name'])
        obj.data = json.dumps(data['data'])
        obj.save()
    except Dataset.DoesNotExist:
        obj = Dataset(
            name=data['name'],
            data=json.dumps(data['data'])
        )
        obj.save()

    try:
        Box.objects.get(x0=data['box'][0], y0=data['box'][1], size=data['box'][2], dataset=obj)
    except Box.DoesNotExist:
        Box(x0=data['box'][0], y0=data['box'][1], size=data['box'][2], dataset=obj).save()

    return HttpResponse("success")


def delete(request):
    data = json.loads(request.body)

    obj = Dataset.objects.get(name=data['name'])
    box = Box.objects.get(x0=data['box'][0], y0=data['box'][1], size=data['box'][2], dataset=obj)
    box.delete()

    return HttpResponse("success")


def results(request):
    all_data = {x.name: json.loads(x.data) for x in Dataset.objects.all()}
    all_boxes = {name: [{'x0': x.x0, 'y0': x.y0, 'size': x.size} for
                        x in Box.objects.filter(dataset=Dataset.objects.get(name=name))]
                 for name in all_data.keys()}
    combined = {'splines': all_data, 'boxes': all_boxes}
    return HttpResponse(json.dumps(combined, indent=2), content_type="application/json")


def show(request):
    # assuming all imgs have same size for now
    img = io.imread(os.path.join(static_dir, folders[0], 'w.png'))
    h, w = img.shape[:2]
    context = {'h': h, 'w': w}
    return render(request, "show.html", context)
