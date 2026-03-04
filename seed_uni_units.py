import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance_system.settings")
django.setup()

from attendance.models import Program, Unit

# =============================================================
# MMU UNITS — Approximate based on standard Kenyan university
# curricula. Verify against your official MMU student handbook
# and correct any unit codes or names as needed.
#
# semester & year key:
#   semester 1, year 1 = Year 1 Sem 1 | semester 2, year 1 = Year 1 Sem 2
#   semester 3, year 2 = Year 2 Sem 1 | semester 4, year 2 = Year 2 Sem 2
#   semester 5, year 3 = Year 3 Sem 1 | semester 6, year 3 = Year 3 Sem 2
#   semester 7, year 4 = Year 4 Sem 1 | semester 8, year 4 = Year 4 Sem 2
#   semester 9, year 5 = Year 5 Sem 1 | semester 10, year 5 = Year 5 Sem 2 (Engineering)
# =============================================================

MMU_UNITS = [

    # =========================================================
    # FoCIT — Bachelor of Science in Computer Science
    # =========================================================
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1101", "name": "Introduction to Computer Science",      "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1102", "name": "Discrete Mathematics",                  "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1103", "name": "Communication Skills",                  "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1104", "name": "Introduction to Programming",           "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1105", "name": "Computer Hardware & Architecture",      "semester": 1, "year": 1},

    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1201", "name": "Data Structures & Algorithms",         "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1202", "name": "Calculus for Computing",               "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1203", "name": "Object Oriented Programming",          "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1204", "name": "Operating Systems I",                  "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 1205", "name": "Database Systems I",                   "semester": 2, "year": 1},

    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2101", "name": "Computer Networks I",                  "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2102", "name": "Software Engineering I",               "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2103", "name": "Database Systems II",                  "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2104", "name": "Systems Analysis & Design",            "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2105", "name": "Statistics for Computing",             "semester": 3, "year": 2},

    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2201", "name": "Computer Networks II",                 "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2202", "name": "Software Engineering II",              "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2203", "name": "Artificial Intelligence",              "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2204", "name": "Web Technologies",                     "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 2205", "name": "Human Computer Interaction",           "semester": 4, "year": 2},

    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3101", "name": "Machine Learning",                     "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3102", "name": "Computer Graphics",                    "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3103", "name": "Information Security",                 "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3104", "name": "Mobile Application Development",       "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3105", "name": "Research Methods",                     "semester": 5, "year": 3},

    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3201", "name": "Cloud Computing",                      "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3202", "name": "Distributed Systems",                  "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3203", "name": "Compiler Construction",                "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 3204", "name": "Industrial Attachment",                "semester": 6, "year": 3},

    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 4101", "name": "Final Year Project I",                 "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 4102", "name": "Entrepreneurship & Innovation",        "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 4103", "name": "Advanced Database Systems",            "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 4104", "name": "Computer Vision",                      "semester": 7, "year": 4},

    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 4201", "name": "Final Year Project II",                "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 4202", "name": "Professional Ethics in Computing",     "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Computer Science", "unit_code": "CCS 4203", "name": "Special Topics in Computer Science",   "semester": 8, "year": 4},

    # =========================================================
    # FoCIT — Bachelor of Science in Information Technology
    # =========================================================
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1101", "name": "Fundamentals of IT",                     "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1102", "name": "Mathematics for IT",                     "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1103", "name": "Communication Skills",                   "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1104", "name": "Introduction to Programming",            "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1105", "name": "Computer Organisation",                  "semester": 1, "year": 1},

    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1201", "name": "Data Structures",                        "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1202", "name": "Web Design & Development",               "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1203", "name": "Database Management Systems",            "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1204", "name": "Operating Systems",                      "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 1205", "name": "Systems Analysis & Design",              "semester": 2, "year": 1},

    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2101", "name": "Computer Networks",                      "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2102", "name": "Object Oriented Programming",            "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2103", "name": "IT Project Management",                  "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2104", "name": "Human Computer Interaction",             "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2105", "name": "Statistics",                             "semester": 3, "year": 2},

    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2201", "name": "Network Administration",                 "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2202", "name": "Information Systems Security",           "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2203", "name": "Software Development",                   "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2204", "name": "E-Commerce",                             "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 2205", "name": "Mobile Computing",                       "semester": 4, "year": 2},

    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3101", "name": "Cloud Computing",                        "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3102", "name": "IT Governance & Compliance",             "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3103", "name": "Enterprise Systems",                     "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3104", "name": "Research Methods",                       "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3105", "name": "Data Analytics",                         "semester": 5, "year": 3},

    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3201", "name": "Industrial Attachment",                  "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3202", "name": "IT Service Management",                  "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3203", "name": "Advanced Networking",                    "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 3204", "name": "Business Intelligence",                  "semester": 6, "year": 3},

    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 4101", "name": "Final Year Project I",                   "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 4102", "name": "IT Entrepreneurship",                    "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 4103", "name": "Emerging Technologies",                  "semester": 7, "year": 4},

    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 4201", "name": "Final Year Project II",                  "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 4202", "name": "Professional Ethics in IT",              "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Information Technology", "unit_code": "CIT 4203", "name": "Special Topics in IT",                   "semester": 8, "year": 4},

    # =========================================================
    # FoCIT — Bachelor of Science in Software Engineering
    # =========================================================
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1101", "name": "Introduction to Software Engineering",    "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1102", "name": "Discrete Mathematics",                   "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1103", "name": "Communication Skills",                   "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1104", "name": "Programming Fundamentals",               "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1105", "name": "Computer Organisation",                  "semester": 1, "year": 1},

    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1201", "name": "Object Oriented Programming",            "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1202", "name": "Data Structures & Algorithms",          "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1203", "name": "Database Design",                       "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1204", "name": "Operating Systems",                     "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 1205", "name": "Calculus & Linear Algebra",             "semester": 2, "year": 1},

    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2101", "name": "Software Requirements Engineering",      "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2102", "name": "Software Architecture & Design",        "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2103", "name": "Web Application Development",           "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2104", "name": "Computer Networks",                     "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2105", "name": "Statistics for Engineers",              "semester": 3, "year": 2},

    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2201", "name": "Software Testing & Quality Assurance",  "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2202", "name": "Mobile Development",                   "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2203", "name": "Human Computer Interaction",            "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2204", "name": "Agile Development",                    "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 2205", "name": "Software Project Management",          "semester": 4, "year": 2},

    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3101", "name": "DevOps & CI/CD",                        "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3102", "name": "Cloud Application Development",        "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3103", "name": "Software Security",                    "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3104", "name": "Research Methods",                     "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3105", "name": "Microservices & APIs",                 "semester": 5, "year": 3},

    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3201", "name": "Industrial Attachment",                "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3202", "name": "Distributed Systems",                  "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 3203", "name": "Artificial Intelligence",              "semester": 6, "year": 3},

    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 4101", "name": "Final Year Project I",                 "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 4102", "name": "Entrepreneurship",                     "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 4103", "name": "Advanced Software Architecture",       "semester": 7, "year": 4},

    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 4201", "name": "Final Year Project II",                "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 4202", "name": "Professional Ethics",                  "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Software Engineering", "unit_code": "CSE 4203", "name": "Special Topics in SE",                 "semester": 8, "year": 4},

    # =========================================================
    # FoCIT — Bachelor of Science in Computer Security
    # =========================================================
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1101", "name": "Introduction to Computer Security",      "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1102", "name": "Discrete Mathematics",                  "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1103", "name": "Communication Skills",                  "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1104", "name": "Introduction to Programming",           "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1105", "name": "Computer Hardware & Architecture",      "semester": 1, "year": 1},

    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1201", "name": "Cryptography Fundamentals",             "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1202", "name": "Operating Systems Security",           "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1203", "name": "Database Systems",                     "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1204", "name": "Networking Fundamentals",              "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 1205", "name": "Programming for Security",             "semester": 2, "year": 1},

    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2101", "name": "Network Security",                     "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2102", "name": "Ethical Hacking",                      "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2103", "name": "Digital Forensics I",                  "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2104", "name": "Secure Software Development",          "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2105", "name": "Statistics",                           "semester": 3, "year": 2},

    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2201", "name": "Digital Forensics II",                 "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2202", "name": "Malware Analysis",                     "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2203", "name": "Cyber Law & Ethics",                   "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2204", "name": "Cloud Security",                       "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 2205", "name": "Intrusion Detection Systems",          "semester": 4, "year": 2},

    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 3101", "name": "Penetration Testing",                  "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 3102", "name": "Security Operations Centre",           "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 3103", "name": "Risk Management",                     "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 3104", "name": "Research Methods",                    "semester": 5, "year": 3},

    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 3201", "name": "Industrial Attachment",               "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 3202", "name": "Advanced Cryptography",               "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 3203", "name": "Mobile Security",                     "semester": 6, "year": 3},

    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 4101", "name": "Final Year Project I",                "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 4102", "name": "Entrepreneurship",                    "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 4103", "name": "Incident Response",                   "semester": 7, "year": 4},

    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 4201", "name": "Final Year Project II",               "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 4202", "name": "Professional Ethics",                 "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Computer Security", "unit_code": "CKS 4203", "name": "Special Topics in Security",          "semester": 8, "year": 4},

    # =========================================================
    # FAMECO — Bachelor of Arts in Journalism
    # =========================================================
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1101", "name": "Introduction to Journalism",              "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1102", "name": "Communication Theory",                   "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1103", "name": "English for Communication",              "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1104", "name": "Introduction to Media Studies",          "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1105", "name": "Basic Photography",                      "semester": 1, "year": 1},

    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1201", "name": "News Writing & Reporting",               "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1202", "name": "Print Media Production",                 "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1203", "name": "Media Law & Ethics",                     "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1204", "name": "Introduction to Broadcasting",           "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 1205", "name": "Digital Media Fundamentals",             "semester": 2, "year": 1},

    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2101", "name": "Broadcast Journalism",                   "semester": 3, "year": 2},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2102", "name": "Feature Writing",                        "semester": 3, "year": 2},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2103", "name": "Photojournalism",                        "semester": 3, "year": 2},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2104", "name": "Online Journalism",                      "semester": 3, "year": 2},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2105", "name": "Research Methods in Media",              "semester": 3, "year": 2},

    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2201", "name": "Investigative Journalism",               "semester": 4, "year": 2},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2202", "name": "TV Production",                          "semester": 4, "year": 2},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2203", "name": "Radio Production",                       "semester": 4, "year": 2},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 2204", "name": "Media Management",                       "semester": 4, "year": 2},

    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 3101", "name": "Data Journalism",                        "semester": 5, "year": 3},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 3102", "name": "Political Journalism",                   "semester": 5, "year": 3},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 3103", "name": "Sports Journalism",                      "semester": 5, "year": 3},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 3104", "name": "Multimedia Journalism",                  "semester": 5, "year": 3},

    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 3201", "name": "Industrial Attachment",                  "semester": 6, "year": 3},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 3202", "name": "Media & Society",                        "semester": 6, "year": 3},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 3203", "name": "Science & Development Journalism",       "semester": 6, "year": 3},

    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 4101", "name": "Final Year Project I",                   "semester": 7, "year": 4},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 4102", "name": "Entrepreneurship in Media",              "semester": 7, "year": 4},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 4103", "name": "Global Media Trends",                    "semester": 7, "year": 4},

    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 4201", "name": "Final Year Project II",                  "semester": 8, "year": 4},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 4202", "name": "Professional Ethics in Journalism",      "semester": 8, "year": 4},
    {"program": "Bachelor of Arts in Journalism", "unit_code": "BJN 4203", "name": "Special Topics in Journalism",           "semester": 8, "year": 4},

    # =========================================================
    # FoET — Bachelor of Science in Electrical Engineering
    # =========================================================
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1101", "name": "Engineering Mathematics I",           "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1102", "name": "Introduction to Engineering",         "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1103", "name": "Communication Skills",                "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1104", "name": "Physics for Engineers",               "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1105", "name": "Engineering Drawing",                 "semester": 1, "year": 1},

    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1201", "name": "Engineering Mathematics II",          "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1202", "name": "Circuit Theory I",                    "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1203", "name": "Electronics I",                       "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1204", "name": "Programming for Engineers",           "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 1205", "name": "Workshop Practice",                   "semester": 2, "year": 1},

    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2101", "name": "Circuit Theory II",                   "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2102", "name": "Electronics II",                      "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2103", "name": "Signals & Systems",                   "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2104", "name": "Electromagnetism",                    "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2105", "name": "Engineering Statistics",              "semester": 3, "year": 2},

    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2201", "name": "Control Systems I",                   "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2202", "name": "Power Systems I",                     "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2203", "name": "Digital Electronics",                 "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2204", "name": "Microprocessors",                     "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 2205", "name": "Instrumentation",                     "semester": 4, "year": 2},

    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 3101", "name": "Control Systems II",                  "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 3102", "name": "Power Systems II",                    "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 3103", "name": "Embedded Systems",                    "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 3104", "name": "Research Methods",                    "semester": 5, "year": 3},

    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 3201", "name": "Industrial Attachment",               "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 3202", "name": "Renewable Energy Systems",            "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 3203", "name": "High Voltage Engineering",            "semester": 6, "year": 3},

    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 4101", "name": "Final Year Project I",                "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 4102", "name": "Engineering Management",             "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 4103", "name": "Smart Grid Technologies",            "semester": 7, "year": 4},

    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 4201", "name": "Final Year Project II",               "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 4202", "name": "Professional Ethics",                 "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 4203", "name": "Special Topics in EE",               "semester": 8, "year": 4},

    # =========================================================
    # FoBE — Bachelor of Business Administration
    # =========================================================
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1101", "name": "Principles of Management",             "semester": 1, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1102", "name": "Business Mathematics",                 "semester": 1, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1103", "name": "Communication Skills",                 "semester": 1, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1104", "name": "Introduction to Economics",            "semester": 1, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1105", "name": "Financial Accounting I",               "semester": 1, "year": 1},

    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1201", "name": "Business Law",                        "semester": 2, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1202", "name": "Marketing Principles",                "semester": 2, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1203", "name": "Financial Accounting II",             "semester": 2, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1204", "name": "Organisational Behaviour",            "semester": 2, "year": 1},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 1205", "name": "Business Statistics",                 "semester": 2, "year": 1},

    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2101", "name": "Human Resource Management",           "semester": 3, "year": 2},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2102", "name": "Management Accounting",               "semester": 3, "year": 2},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2103", "name": "Operations Management",               "semester": 3, "year": 2},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2104", "name": "Business Information Systems",        "semester": 3, "year": 2},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2105", "name": "Research Methods",                    "semester": 3, "year": 2},

    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2201", "name": "Strategic Management",                "semester": 4, "year": 2},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2202", "name": "Financial Management",                "semester": 4, "year": 2},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2203", "name": "Supply Chain Management",             "semester": 4, "year": 2},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 2204", "name": "Entrepreneurship",                    "semester": 4, "year": 2},

    {"program": "Bachelor of Business Administration", "unit_code": "BBA 3101", "name": "International Business",              "semester": 5, "year": 3},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 3102", "name": "Project Management",                  "semester": 5, "year": 3},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 3103", "name": "Corporate Governance",                "semester": 5, "year": 3},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 3104", "name": "Digital Marketing",                   "semester": 5, "year": 3},

    {"program": "Bachelor of Business Administration", "unit_code": "BBA 3201", "name": "Industrial Attachment",               "semester": 6, "year": 3},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 3202", "name": "Business Ethics",                     "semester": 6, "year": 3},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 3203", "name": "Risk Management",                     "semester": 6, "year": 3},

    {"program": "Bachelor of Business Administration", "unit_code": "BBA 4101", "name": "Final Year Project I",                "semester": 7, "year": 4},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 4102", "name": "Leadership & Change Management",      "semester": 7, "year": 4},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 4103", "name": "E-Business",                          "semester": 7, "year": 4},

    {"program": "Bachelor of Business Administration", "unit_code": "BBA 4201", "name": "Final Year Project II",               "semester": 8, "year": 4},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 4202", "name": "Professional Ethics in Business",     "semester": 8, "year": 4},
    {"program": "Bachelor of Business Administration", "unit_code": "BBA 4203", "name": "Special Topics in BBA",               "semester": 8, "year": 4},

    # =========================================================
    # FoST — Bachelor of Science in Mathematics
    # =========================================================
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1101", "name": "Calculus I",                           "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1102", "name": "Linear Algebra",                       "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1103", "name": "Communication Skills",                 "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1104", "name": "Logic & Set Theory",                   "semester": 1, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1105", "name": "Introduction to Computing",            "semester": 1, "year": 1},

    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1201", "name": "Calculus II",                          "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1202", "name": "Abstract Algebra",                     "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1203", "name": "Probability Theory",                   "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1204", "name": "Numerical Methods",                    "semester": 2, "year": 1},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 1205", "name": "Statistics I",                         "semester": 2, "year": 1},

    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2101", "name": "Real Analysis",                        "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2102", "name": "Differential Equations",               "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2103", "name": "Statistics II",                        "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2104", "name": "Graph Theory",                         "semester": 3, "year": 2},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2105", "name": "Mathematical Modelling",               "semester": 3, "year": 2},

    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2201", "name": "Complex Analysis",                     "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2202", "name": "Topology",                             "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2203", "name": "Operations Research",                  "semester": 4, "year": 2},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 2204", "name": "Mathematical Statistics",              "semester": 4, "year": 2},

    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 3101", "name": "Functional Analysis",                  "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 3102", "name": "Number Theory",                        "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 3103", "name": "Research Methods",                     "semester": 5, "year": 3},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 3104", "name": "Data Analysis",                        "semester": 5, "year": 3},

    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 3201", "name": "Industrial Attachment",                "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 3202", "name": "Partial Differential Equations",       "semester": 6, "year": 3},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 3203", "name": "Financial Mathematics",                "semester": 6, "year": 3},

    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 4101", "name": "Final Year Project I",                 "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 4102", "name": "Actuarial Mathematics",                "semester": 7, "year": 4},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 4103", "name": "Cryptography",                         "semester": 7, "year": 4},

    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 4201", "name": "Final Year Project II",                "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 4202", "name": "Professional Ethics",                  "semester": 8, "year": 4},
    {"program": "Bachelor of Science in Mathematics", "unit_code": "MTH 4203", "name": "Special Topics in Mathematics",        "semester": 8, "year": 4},


    # Year 5, Semester 1 (Engineering only — 5 year program)
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 5101", "name": "Advanced Power Electronics",          "semester": 9,  "year": 5},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 5102", "name": "Telecommunications Systems",          "semester": 9,  "year": 5},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 5103", "name": "Engineering Project Management",      "semester": 9,  "year": 5},

    # Year 5, Semester 2 (Engineering only — 5 year program)
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 5201", "name": "Final Year Project I",                "semester": 10, "year": 5},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 5202", "name": "Final Year Project II",               "semester": 10, "year": 5},
    {"program": "Bachelor of Science in Electrical Engineering", "unit_code": "EEE 5203", "name": "Professional Engineering Practice",   "semester": 10, "year": 5},

    # =========================================================
    # FoSST — Bachelor of Arts in Sociology
    # =========================================================
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1101", "name": "Introduction to Sociology",                "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1102", "name": "Social Theory I",                          "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1103", "name": "Communication Skills",                     "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1104", "name": "Introduction to Psychology",               "semester": 1, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1105", "name": "Introduction to Statistics",               "semester": 1, "year": 1},

    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1201", "name": "Social Theory II",                         "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1202", "name": "Research Methods in Social Sciences",      "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1203", "name": "African Sociology",                        "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1204", "name": "Social Psychology",                        "semester": 2, "year": 1},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 1205", "name": "Introduction to Anthropology",             "semester": 2, "year": 1},

    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2101", "name": "Sociology of Education",                   "semester": 3, "year": 2},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2102", "name": "Sociology of Health",                      "semester": 3, "year": 2},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2103", "name": "Gender & Society",                         "semester": 3, "year": 2},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2104", "name": "Political Sociology",                      "semester": 3, "year": 2},

    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2201", "name": "Urban Sociology",                          "semester": 4, "year": 2},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2202", "name": "Sociology of Development",                 "semester": 4, "year": 2},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2203", "name": "Qualitative Research Methods",             "semester": 4, "year": 2},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 2204", "name": "Community Development",                    "semester": 4, "year": 2},

    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 3101", "name": "Criminology",                              "semester": 5, "year": 3},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 3102", "name": "Social Policy",                            "semester": 5, "year": 3},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 3103", "name": "Research Methods II",                      "semester": 5, "year": 3},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 3104", "name": "Sociology of Religion",                    "semester": 5, "year": 3},

    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 3201", "name": "Industrial Attachment",                    "semester": 6, "year": 3},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 3202", "name": "Environmental Sociology",                  "semester": 6, "year": 3},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 3203", "name": "Media & Society",                          "semester": 6, "year": 3},

    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 4101", "name": "Final Year Project I",                     "semester": 7, "year": 4},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 4102", "name": "Social Entrepreneurship",                  "semester": 7, "year": 4},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 4103", "name": "Globalisation & Society",                  "semester": 7, "year": 4},

    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 4201", "name": "Final Year Project II",                    "semester": 8, "year": 4},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 4202", "name": "Professional Ethics",                      "semester": 8, "year": 4},
    {"program": "Bachelor of Arts in Sociology", "unit_code": "SOC 4203", "name": "Special Topics in Sociology",              "semester": 8, "year": 4},
]


def seed():
    created_count = 0
    skipped_count = 0
    error_count   = 0

    for data in MMU_UNITS:
        try:
            program = Program.objects.get(course=data["program"])
            obj, created = Unit.objects.get_or_create(
                unit_code=data["unit_code"],
                program=program,
                defaults={
                    "name":     data["name"],
                    "semester": data["semester"],
                    "year":     data["year"],
                },
            )
            if created:
                print(f"  ✅ Created : [{obj.unit_code}] {obj.name} — Year {obj.year} Sem {obj.semester}")
                created_count += 1
            else:
                print(f"  ⏭️  Exists  : [{obj.unit_code}] {obj.name}")
                skipped_count += 1

        except Program.DoesNotExist:
            print(f"  ❌ Program not found: '{data['program']}' — run seed_uni_data.py first.")
            error_count += 1

    print(f"\nDone. {created_count} created, {skipped_count} already existed, {error_count} errors.")


if __name__ == "__main__":
    print("Seeding MMU units...\n")
    seed()
