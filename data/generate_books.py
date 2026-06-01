"""
Generator cho dataset thư viện (data/books.json).

Dùng danh sách sách THẬT (title/author/category) rồi gán ngẫu nhiên có seed cho
total_copies, available_copies, late_fee_per_day -> dataset ổn định, tái lập được.

Chạy:  python data/generate_books.py
"""
import json
import os
import random

# (title, author, category)
BOOKS = [
    # --- Software Engineering ---
    ("Clean Code", "Robert C. Martin", "Software Engineering"),
    ("The Pragmatic Programmer", "Andrew Hunt, David Thomas", "Software Engineering"),
    ("Refactoring", "Martin Fowler", "Software Engineering"),
    ("Design Patterns", "Gamma, Helm, Johnson, Vlissides", "Software Engineering"),
    ("Code Complete", "Steve McConnell", "Software Engineering"),
    ("The Mythical Man-Month", "Frederick P. Brooks Jr.", "Software Engineering"),
    ("Clean Architecture", "Robert C. Martin", "Software Engineering"),
    ("Working Effectively with Legacy Code", "Michael Feathers", "Software Engineering"),
    ("Domain-Driven Design", "Eric Evans", "Software Engineering"),
    ("Patterns of Enterprise Application Architecture", "Martin Fowler", "Software Engineering"),
    ("The Clean Coder", "Robert C. Martin", "Software Engineering"),
    ("Release It!", "Michael T. Nygard", "Software Engineering"),
    ("Continuous Delivery", "Jez Humble, David Farley", "Software Engineering"),
    ("The Phoenix Project", "Gene Kim, Kevin Behr, George Spafford", "Software Engineering"),
    ("Accelerate", "Nicole Forsgren, Jez Humble, Gene Kim", "Software Engineering"),
    ("Software Engineering at Google", "Titus Winters, Tom Manshreck, Hyrum Wright", "Software Engineering"),
    ("A Philosophy of Software Design", "John Ousterhout", "Software Engineering"),
    ("Head First Design Patterns", "Eric Freeman, Elisabeth Robson", "Software Engineering"),
    ("Test-Driven Development by Example", "Kent Beck", "Software Engineering"),
    ("Extreme Programming Explained", "Kent Beck", "Software Engineering"),

    # --- Computer Science ---
    ("Structure and Interpretation of Computer Programs", "Harold Abelson, Gerald Jay Sussman", "Computer Science"),
    ("The Art of Computer Programming", "Donald E. Knuth", "Computer Science"),
    ("Computer Systems: A Programmer's Perspective", "Randal Bryant, David O'Hallaron", "Computer Science"),
    ("Operating System Concepts", "Abraham Silberschatz, Peter Galvin, Greg Gagne", "Computer Science"),
    ("Modern Operating Systems", "Andrew S. Tanenbaum", "Computer Science"),
    ("Computer Networks", "Andrew S. Tanenbaum", "Computer Science"),
    ("Computer Organization and Design", "David Patterson, John Hennessy", "Computer Science"),
    ("Compilers: Principles, Techniques, and Tools", "Aho, Lam, Sethi, Ullman", "Computer Science"),
    ("Introduction to the Theory of Computation", "Michael Sipser", "Computer Science"),
    ("Operating Systems: Three Easy Pieces", "Remzi Arpaci-Dusseau, Andrea Arpaci-Dusseau", "Computer Science"),

    # --- Algorithms ---
    ("Introduction to Algorithms", "Cormen, Leiserson, Rivest, Stein", "Algorithms"),
    ("Algorithms", "Robert Sedgewick, Kevin Wayne", "Algorithms"),
    ("The Algorithm Design Manual", "Steven Skiena", "Algorithms"),
    ("Algorithm Design", "Jon Kleinberg, Eva Tardos", "Algorithms"),
    ("Grokking Algorithms", "Aditya Bhargava", "Algorithms"),
    ("Cracking the Coding Interview", "Gayle Laakmann McDowell", "Algorithms"),
    ("Programming Pearls", "Jon Bentley", "Algorithms"),
    ("Competitive Programming", "Steven Halim, Felix Halim", "Algorithms"),

    # --- Programming Languages ---
    ("You Don't Know JS", "Kyle Simpson", "Programming Languages"),
    ("Eloquent JavaScript", "Marijn Haverbeke", "Programming Languages"),
    ("JavaScript: The Good Parts", "Douglas Crockford", "Programming Languages"),
    ("Effective Java", "Joshua Bloch", "Programming Languages"),
    ("Java Concurrency in Practice", "Brian Goetz", "Programming Languages"),
    ("Effective C++", "Scott Meyers", "Programming Languages"),
    ("The C Programming Language", "Brian Kernighan, Dennis Ritchie", "Programming Languages"),
    ("The C++ Programming Language", "Bjarne Stroustrup", "Programming Languages"),
    ("Programming Rust", "Jim Blandy, Jason Orendorff", "Programming Languages"),
    ("The Rust Programming Language", "Steve Klabnik, Carol Nichols", "Programming Languages"),
    ("Fluent Python", "Luciano Ramalho", "Programming Languages"),
    ("Python Crash Course", "Eric Matthes", "Programming Languages"),
    ("Effective Python", "Brett Slatkin", "Programming Languages"),
    ("Learning Python", "Mark Lutz", "Programming Languages"),
    ("The Go Programming Language", "Alan Donovan, Brian Kernighan", "Programming Languages"),
    ("Programming Elixir", "Dave Thomas", "Programming Languages"),
    ("Land of Lisp", "Conrad Barski", "Programming Languages"),
    ("The Little Schemer", "Daniel Friedman, Matthias Felleisen", "Programming Languages"),
    ("Programming Ruby", "Dave Thomas, Andy Hunt, Chad Fowler", "Programming Languages"),
    ("Kotlin in Action", "Dmitry Jemerov, Svetlana Isakova", "Programming Languages"),

    # --- AI / ML ---
    ("Artificial Intelligence: A Modern Approach", "Stuart Russell, Peter Norvig", "AI & Machine Learning"),
    ("Deep Learning", "Ian Goodfellow, Yoshua Bengio, Aaron Courville", "AI & Machine Learning"),
    ("Pattern Recognition and Machine Learning", "Christopher Bishop", "AI & Machine Learning"),
    ("The Elements of Statistical Learning", "Hastie, Tibshirani, Friedman", "AI & Machine Learning"),
    ("Hands-On Machine Learning", "Aurelien Geron", "AI & Machine Learning"),
    ("Machine Learning", "Tom Mitchell", "AI & Machine Learning"),
    ("Reinforcement Learning: An Introduction", "Richard Sutton, Andrew Barto", "AI & Machine Learning"),
    ("Deep Learning with Python", "Francois Chollet", "AI & Machine Learning"),
    ("Grokking Deep Learning", "Andrew Trask", "AI & Machine Learning"),
    ("Speech and Language Processing", "Daniel Jurafsky, James Martin", "AI & Machine Learning"),
    ("Probabilistic Machine Learning", "Kevin Murphy", "AI & Machine Learning"),
    ("Dive into Deep Learning", "Aston Zhang, Zachary Lipton, Mu Li", "AI & Machine Learning"),

    # --- Data ---
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Data"),
    ("Database System Concepts", "Silberschatz, Korth, Sudarshan", "Data"),
    ("SQL Performance Explained", "Markus Winand", "Data"),
    ("Big Data", "Nathan Marz, James Warren", "Data"),
    ("Data Science from Scratch", "Joel Grus", "Data"),
    ("Python for Data Analysis", "Wes McKinney", "Data"),
    ("Storytelling with Data", "Cole Nussbaumer Knaflic", "Data"),
    ("The Data Warehouse Toolkit", "Ralph Kimball, Margy Ross", "Data"),

    # --- Security ---
    ("The Web Application Hacker's Handbook", "Dafydd Stuttard, Marcus Pinto", "Security"),
    ("Hacking: The Art of Exploitation", "Jon Erickson", "Security"),
    ("Applied Cryptography", "Bruce Schneier", "Security"),
    ("Security Engineering", "Ross Anderson", "Security"),
    ("The Tangled Web", "Michal Zalewski", "Security"),
    ("Practical Malware Analysis", "Michael Sikorski, Andrew Honig", "Security"),
    ("Cryptography Engineering", "Ferguson, Schneier, Kohno", "Security"),

    # --- Systems / Networking / DevOps ---
    ("TCP/IP Illustrated", "W. Richard Stevens", "Systems & Networking"),
    ("Unix Network Programming", "W. Richard Stevens", "Systems & Networking"),
    ("The Linux Programming Interface", "Michael Kerrisk", "Systems & Networking"),
    ("Site Reliability Engineering", "Beyer, Jones, Petoff, Murphy", "Systems & Networking"),
    ("Kubernetes Up & Running", "Kelsey Hightower, Brendan Burns, Joe Beda", "Systems & Networking"),
    ("Docker Deep Dive", "Nigel Poulton", "Systems & Networking"),
    ("The DevOps Handbook", "Gene Kim, Jez Humble, Patrick Debois", "Systems & Networking"),
    ("Linux Kernel Development", "Robert Love", "Systems & Networking"),
    ("Systems Performance", "Brendan Gregg", "Systems & Networking"),

    # --- Mathematics ---
    ("Concrete Mathematics", "Graham, Knuth, Patashnik", "Mathematics"),
    ("Linear Algebra Done Right", "Sheldon Axler", "Mathematics"),
    ("Mathematics for Machine Learning", "Deisenroth, Faisal, Ong", "Mathematics"),
    ("How to Prove It", "Daniel Velleman", "Mathematics"),
    ("Discrete Mathematics and Its Applications", "Kenneth Rosen", "Mathematics"),
    ("Calculus", "Michael Spivak", "Mathematics"),

    # --- Business / Product ---
    ("The Lean Startup", "Eric Ries", "Business & Product"),
    ("Inspired", "Marty Cagan", "Business & Product"),
    ("Hooked", "Nir Eyal", "Business & Product"),
    ("Zero to One", "Peter Thiel, Blake Masters", "Business & Product"),
    ("The Hard Thing About Hard Things", "Ben Horowitz", "Business & Product"),
    ("Crossing the Chasm", "Geoffrey Moore", "Business & Product"),

    # --- General / History ---
    ("Godel, Escher, Bach", "Douglas Hofstadter", "General & History"),
    ("The Soul of a New Machine", "Tracy Kidder", "General & History"),
    ("Hackers", "Steven Levy", "General & History"),
    ("The Code Book", "Simon Singh", "General & History"),
    ("Coders at Work", "Peter Seibel", "General & History"),
    ("The Innovators", "Walter Isaacson", "General & History"),
    ("The Pragmatic Thinking and Learning", "Andy Hunt", "General & History"),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "General & History"),
]

# Khoảng phí phạt trễ hạn (VND/ngày) theo category.
LATE_FEE_BY_CATEGORY = {
    "Software Engineering": [4000, 5000, 6000],
    "Computer Science": [6000, 7000, 8000],
    "Algorithms": [7000, 8000, 9000],
    "Programming Languages": [3000, 4000, 5000],
    "AI & Machine Learning": [8000, 9000, 10000],
    "Data": [6000, 7000, 8000],
    "Security": [7000, 8000, 9000],
    "Systems & Networking": [6000, 7000, 8000],
    "Mathematics": [5000, 6000, 7000],
    "Business & Product": [3000, 4000],
    "General & History": [3000, 4000, 5000],
}


# Tu khoa chu de theo category -> dung cho semantic_search & recommend_books.
TOPICS_BY_CATEGORY = {
    "Software Engineering": ["clean code", "refactoring", "design patterns", "architecture", "best practices", "testing"],
    "Computer Science": ["operating systems", "computer architecture", "compilers", "theory", "systems"],
    "Algorithms": ["algorithms", "data structures", "problem solving", "complexity", "interview prep"],
    "Programming Languages": ["language design", "syntax", "concurrency", "memory", "idioms"],
    "AI & Machine Learning": ["machine learning", "deep learning", "neural networks", "statistics", "nlp"],
    "Data": ["databases", "data engineering", "sql", "big data", "data analysis"],
    "Security": ["cryptography", "exploitation", "web security", "malware", "threat modeling"],
    "Systems & Networking": ["networking", "linux", "devops", "kubernetes", "performance"],
    "Mathematics": ["linear algebra", "discrete math", "calculus", "proofs", "math for ml"],
    "Business & Product": ["startup", "product management", "strategy", "growth", "leadership"],
    "General & History": ["computing history", "hacker culture", "biography", "thinking", "essays"],
}

LEVELS = ["beginner", "intermediate", "advanced"]


def _make_description(rng, title, author, category, topics, level):
    """Sinh mo ta ngan (2-3 cau) cho semantic search."""
    t1, t2 = topics[0], topics[1] if len(topics) > 1 else topics[0]
    templates = [
        f"'{title}' by {author} is a {level} book on {category.lower()}, focusing on {t1} and {t2}.",
        f"A {level}-level guide covering {t1}, {t2} and related ideas in {category.lower()}.",
        f"Written by {author}, this {level} title explores {t1} and practical {t2}.",
    ]
    extra = [
        " A widely cited classic in its field.",
        " Recommended for hands-on practitioners.",
        " Balances theory with real-world examples.",
        " Often used in university courses.",
        "",
    ]
    return rng.choice(templates) + rng.choice(extra)


def build_dataset():
    rng = random.Random(42)  # seed cố định -> tái lập
    records = []
    for i, (title, author, category) in enumerate(BOOKS, start=1):
        total = rng.randint(2, 8)
        available = rng.randint(0, total)  # cho phép 0 -> test nhánh "hết sách"
        fee = rng.choice(LATE_FEE_BY_CATEGORY[category])

        pool = TOPICS_BY_CATEGORY[category]
        topics = rng.sample(pool, k=min(3, len(pool)))
        level = rng.choice(LEVELS)
        description = _make_description(rng, title, author, category, topics, level)

        records.append({
            "id": f"B{i:03d}",
            "title": title,
            "author": author,
            "total_copies": total,
            "available_copies": available,
            "late_fee_per_day": fee,
            "category": category,
            "topics": topics,
            "level": level,
            "year": rng.randint(1995, 2023),
            "pages": rng.randint(180, 1200),
            "rating": round(rng.uniform(3.5, 5.0), 1),
            "description": description,
        })
    return records


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "books.json")
    data = build_dataset()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_titles = len(data)
    out_of_stock = sum(1 for b in data if b["available_copies"] == 0)
    categories = sorted({b["category"] for b in data})
    print(f"Wrote {total_titles} books -> {out_path}")
    print(f"Out of stock (available_copies=0): {out_of_stock}")
    print(f"Categories ({len(categories)}): {', '.join(categories)}")


if __name__ == "__main__":
    main()
