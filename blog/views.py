from django.shortcuts import render

# Home Page View
def home(request):
    return render(request, 'index.html')

# Calculator Store - Blog Page View
def calculator_list(request):
    posts = [
        {
            "id": 1,
            "title": "Best Scientific Calculators for Students",
            "description": "Discover the top scientific calculators ideal for students in 2025.",
            "image": "https://c02.purpledshub.com/uploads/sites/41/2023/01/Untitled-design-1-148f985.jpg?webp=1&w=1200",
            "buy_url": "https://www.sciencefocus.com/buyers-guides/the-best-scientific-calculators",
            "price": 29.99
        },
        {
            "id": 2,
            "title": "Top Graphing Calculators for Engineers",
            "description": "Explore the best graphing calculators designed for engineers and professionals.",
            "image": "https://www.weareteachers.com/wp-content/uploads/best-graphing-calculators-texas-instruments-ti84.jpg",
            "buy_url": "https://www.weareteachers.com/best-graphing-calculators/",
            "price": 99.99
        },
        {
            "id": 3,
            "title": "Affordable Basic Calculators for Daily Use",
            "description": "Check out the best budget-friendly calculators for simple calculations.",
            "image": "https://target.scene7.com/is/image/Target/GUEST_0c56cac8-30ca-48a3-aa8c-a0fa43b23faf?qlt=85&fmt=webp&hei=500&wid=500",
            "buy_url": "https://www.target.com/p/casio-desktop-business-caculator/-/A-78175313#lnk=sametab",
            "price": 12.99
        },
    ]
    return render(request, 'blog.html', {'posts': posts})
