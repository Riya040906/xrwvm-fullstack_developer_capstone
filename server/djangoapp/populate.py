from .models import CarMake, CarModel


def initiate():
    makes = [
        ("NISSAN", "Japanese technology", ["Pathfinder", "Qashqai", "Altima"]),
        ("Mercedes", "German engineering", ["A-Class", "C-Class", "E-Class"]),
        ("Audi", "German engineering", ["A4", "Q5", "A6"]),
        ("Kia", "Korean design", ["Sportage", "Sorento", "Cerato"]),
        ("Toyota", "Japanese reliability", ["Corolla", "Camry", "Highlander"]),
    ]

    for make_name, description, model_names in makes:
        make, _ = CarMake.objects.get_or_create(
            name=make_name,
            defaults={"description": description},
        )
        for model_name in model_names:
            CarModel.objects.get_or_create(
                car_make=make,
                name=model_name,
                defaults={"type": "SUV", "year": 2023},
            )