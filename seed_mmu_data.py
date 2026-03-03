import os
import django

# --- Bootstrap Django before importing models ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance_system.settings")
django.setup()

from attendance.models import Program

# --- MMU Programs by Faculty ---
MMU_PROGRAMS = [
    # FoCIT — Faculty of Computing and Information Technology
    {"faculty": "FoCIT", "course": "Bachelor of Science in Computer Science",          "department": "Computer Science"},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Information Technology",    "department": "Information Technology"},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Software Engineering",      "department": "Software Engineering"},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Computer Security",         "department": "Computer Security"},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Business Information Tech", "department": "Business IT"},

    # FAMECO — Faculty of Media and Economics
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Journalism",                  "department": "Journalism"},
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Film and Theatre Arts",       "department": "Film & Theatre"},
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Public Relations",            "department": "Public Relations"},
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Communication Studies",       "department": "Communication"},
    {"faculty": "FAMECO", "course": "Bachelor of Economics",                           "department": "Economics"},

    # FoET — Faculty of Engineering and Technology
    {"faculty": "FoET", "course": "Bachelor of Science in Electrical Engineering",     "department": "Electrical Engineering"},
    {"faculty": "FoET", "course": "Bachelor of Science in Telecommunication Eng",      "department": "Telecommunication"},
    {"faculty": "FoET", "course": "Bachelor of Science in Mechanical Engineering",     "department": "Mechanical Engineering"},
    {"faculty": "FoET", "course": "Bachelor of Science in Civil Engineering",          "department": "Civil Engineering"},

    # FoBE — Faculty of Business and Economics
    {"faculty": "FoBE", "course": "Bachelor of Commerce",                              "department": "Commerce"},
    {"faculty": "FoBE", "course": "Bachelor of Business Administration",               "department": "Business Administration"},
    {"faculty": "FoBE", "course": "Bachelor of Science in Accounting",                 "department": "Accounting"},
    {"faculty": "FoBE", "course": "Bachelor of Science in Finance",                    "department": "Finance"},

    # FoST — Faculty of Science and Technology
    {"faculty": "FoST", "course": "Bachelor of Science in Mathematics",                "department": "Mathematics"},
    {"faculty": "FoST", "course": "Bachelor of Science in Physics",                    "department": "Physics"},
    {"faculty": "FoST", "course": "Bachelor of Science in Statistics",                 "department": "Statistics"},
    {"faculty": "FoST", "course": "Bachelor of Science in Biochemistry",               "department": "Biochemistry"},

    # FoSST — Faculty of Social Sciences and Technology
    {"faculty": "FoSST", "course": "Bachelor of Arts in Sociology",                    "department": "Sociology"},
    {"faculty": "FoSST", "course": "Bachelor of Arts in Psychology",                   "department": "Psychology"},
    {"faculty": "FoSST", "course": "Bachelor of Arts in Criminology",                  "department": "Criminology"},
    {"faculty": "FoSST", "course": "Bachelor of Arts in Political Science",            "department": "Political Science"},
]


def seed():
    created_count = 0
    skipped_count = 0

    for data in MMU_PROGRAMS:
        obj, created = Program.objects.get_or_create(
            course=data["course"],
            faculty=data["faculty"],
            defaults={"department": data["department"]},
        )
        if created:
            print(f"  ✅ Created : {obj}")
            created_count += 1
        else:
            print(f"  ⏭️  Exists  : {obj}")
            skipped_count += 1

    print(f"\nDone. {created_count} created, {skipped_count} already existed.")


if __name__ == "__main__":
    print("Seeding MMU programs...\n")
    seed()