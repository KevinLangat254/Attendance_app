import os
import django

# --- Bootstrap Django before importing models ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance_system.settings")
django.setup()

from attendance.models import Program

# --- MMU Programs by Faculty ---
MMU_PROGRAMS = [
    # FoCIT — Faculty of Computing and Information Technology (4 years)
    {"faculty": "FoCIT", "course": "Bachelor of Science in Computer Science",          "department": "Computer Science",       "duration_years": 4},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Information Technology",    "department": "Information Technology", "duration_years": 4},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Software Engineering",      "department": "Software Engineering",   "duration_years": 4},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Computer Security",         "department": "Computer Security",      "duration_years": 4},
    {"faculty": "FoCIT", "course": "Bachelor of Science in Business Information Tech", "department": "Business IT",            "duration_years": 4},

    # FAMECO — Faculty of Media and Economics (4 years)
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Journalism",                  "department": "Journalism",             "duration_years": 4},
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Film and Theatre Arts",       "department": "Film & Theatre",         "duration_years": 4},
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Public Relations",            "department": "Public Relations",       "duration_years": 4},
    {"faculty": "FAMECO", "course": "Bachelor of Arts in Communication Studies",       "department": "Communication",          "duration_years": 4},
    {"faculty": "FAMECO", "course": "Bachelor of Economics",                           "department": "Economics",              "duration_years": 4},

    # FoET — Faculty of Engineering and Technology (5 years)
    {"faculty": "FoET", "course": "Bachelor of Science in Electrical Engineering",     "department": "Electrical Engineering", "duration_years": 5},
    {"faculty": "FoET", "course": "Bachelor of Science in Telecommunication Eng",      "department": "Telecommunication",      "duration_years": 5},
    {"faculty": "FoET", "course": "Bachelor of Science in Mechanical Engineering",     "department": "Mechanical Engineering", "duration_years": 5},
    {"faculty": "FoET", "course": "Bachelor of Science in Civil Engineering",          "department": "Civil Engineering",      "duration_years": 5},

    # FoBE — Faculty of Business and Economics (4 years)
    {"faculty": "FoBE", "course": "Bachelor of Commerce",                              "department": "Commerce",               "duration_years": 4},
    {"faculty": "FoBE", "course": "Bachelor of Business Administration",               "department": "Business Administration","duration_years": 4},
    {"faculty": "FoBE", "course": "Bachelor of Science in Accounting",                 "department": "Accounting",             "duration_years": 4},
    {"faculty": "FoBE", "course": "Bachelor of Science in Finance",                    "department": "Finance",                "duration_years": 4},

    # FoST — Faculty of Science and Technology (4 years)
    {"faculty": "FoST", "course": "Bachelor of Science in Mathematics",                "department": "Mathematics",            "duration_years": 4},
    {"faculty": "FoST", "course": "Bachelor of Science in Physics",                    "department": "Physics",                "duration_years": 4},
    {"faculty": "FoST", "course": "Bachelor of Science in Statistics",                 "department": "Statistics",             "duration_years": 4},
    {"faculty": "FoST", "course": "Bachelor of Science in Biochemistry",               "department": "Biochemistry",           "duration_years": 4},

    # FoSST — Faculty of Social Sciences and Technology (4 years)
    {"faculty": "FoSST", "course": "Bachelor of Arts in Sociology",                    "department": "Sociology",              "duration_years": 4},
    {"faculty": "FoSST", "course": "Bachelor of Arts in Psychology",                   "department": "Psychology",             "duration_years": 4},
    {"faculty": "FoSST", "course": "Bachelor of Arts in Criminology",                  "department": "Criminology",            "duration_years": 4},
    {"faculty": "FoSST", "course": "Bachelor of Arts in Political Science",            "department": "Political Science",      "duration_years": 4},
]


def seed():
    created_count = 0
    skipped_count = 0

    for data in MMU_PROGRAMS:
        obj, created = Program.objects.get_or_create(
            course=data["course"],
            faculty=data["faculty"],
            defaults={
                "department":    data["department"],
                "duration_years": data["duration_years"],
            },
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
