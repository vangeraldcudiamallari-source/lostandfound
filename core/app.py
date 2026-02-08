from flask import Flask, render_template, request

app = Flask(__name__)

# Updated mock database with new fields for Brand and Images
DATABASE = [
    {
        "id": 1,
        "type": "Lost",
        "status": "Active",
        "title": "iPhone 13 Pro",
        "brand": "Apple",
        "location": "Central Park, North Entrance",
        "date": "Oct 24, 2023",
        "color": "Graphite",
        "image_url": "https://images.unsplash.com/photo-1633113089631-6456cccaadad?auto=format&fit=crop&w=400"
    },
    {
        "id": 2,
        "type": "Found",
        "status": "Resolved",
        "title": "Golden Retriever",
        "brand": "N/A",
        "location": "Main St. Library",
        "date": "Oct 23, 2023",
        "color": "Golden/Tan",
        "image_url": "https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=400"
    },
    {
        "id": 3,
        "type": "Lost",
        "status": "Active",
        "title": "Leather Wallet",
        "brand": "Fossil",
        "location": "Downtown Cafe",
        "date": "Oct 25, 2023",
        "color": "Brown",
        "image_url": "https://images.unsplash.com/photo-1627123430984-71511aa7ed50?auto=format&fit=crop&w=400"
    },
    {
        "id": 4,
        "type": "Lost",
        "status": "Active",
        "title": "Phone",
        "brand": "IP17 ProMax",
        "location": "Richwell",
        "date": "March 12, 2025",
        "color": "Orange",
        "image_url": "https://images.unsplash.com/photo-1616348436168-de43ad0db179?auto=format&fit=crop&w=400"
    }
]

@app.route('/')
def home():
    # 1. Capture user input from the URL
    query = request.args.get('search', '').lower()
    category = request.args.get('type', 'all').lower()
    status_filter = request.args.get('status', 'all').lower()

    # 2. Start with all items
    filtered_items = DATABASE

    # 3. Filter by text (Title, Location, Color, or Brand)
    if query:
        filtered_items = [
            item for item in filtered_items 
            if query in item['title'].lower() or 
               query in item['location'].lower() or 
               query in item['color'].lower() or
               query in item.get('brand', '').lower()
        ]

    # 4. Filter by Category (Lost vs Found)
    if category != 'all':
        filtered_items = [
            item for item in filtered_items 
            if item['type'].lower() == category
        ]

    # 5. Filter by Status (Active vs Resolved)
    if status_filter != 'all':
        # "active" in dropdown matches "Active" in DB
        filtered_items = [
            item for item in filtered_items 
            if item['status'].lower() == status_filter
        ]

    return render_template('index.html', items=filtered_items)

if __name__ == '__main__':
    app.run(debug=True)