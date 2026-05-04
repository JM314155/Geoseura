import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        if title not in classes:
            classes[title] = []
        classes[title].append(value)
    return classes

def add_item(title, description, coordinates, created_date, user_id, loc_title, loc_value):
    sql = """INSERT INTO items (title, description, coordinates, created_date, user_id)
             VALUES (?, ?, ?, ?, ?)"""
    item_id = db.execute(sql, [title, description, coordinates, created_date, user_id])

    sql_class = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ?, ?)"
    db.execute(sql_class, [item_id, loc_title, loc_value])
    
    return item_id

def add_visit(item_id, user_id, visit_date):
    sql = """INSERT INTO visits (item_id, user_id, visit_date)
             VALUES (?, ?, ?)"""
    db.execute(sql, [item_id, user_id, visit_date])

def get_visits(item_id):
    sql = """SELECT visits.visit_date, users.id user_id, users.username
             FROM visits
             JOIN users ON visits.user_id = users.id
             WHERE visits.item_id = ?
             ORDER BY visits.visit_date DESC, visits.id DESC"""
    return db.query(sql, [item_id])

def get_cache_creation_date(item_id):
    sql = "SELECT created_date FROM items WHERE id = ?"
    result = db.query(sql, [item_id])
    return result[0][0] if result else None

def get_images(item_id):
    sql = "SELECT id FROM images WHERE item_id = ?"
    return db.query(sql, [item_id])

def add_image(item_id, image):
    sql = "INSERT INTO images (item_id, image) VALUES (?, ?)"
    db.execute(sql, [item_id, image])

def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(item_id, image_id):
    sql = "DELETE FROM images WHERE id = ? AND item_id = ?"
    db.execute(sql, [image_id, item_id])

def get_location(item_id):
    sql = "SELECT title, value FROM item_classes WHERE item_id = ?"
    res = db.query(sql, [item_id])
    return res[0] if res else None

def get_items():
    sql = """SELECT items.id, items.title, users.id user_id, users.username,
                    COUNT(visits.id) visit_count
             FROM items 
             JOIN users ON items.user_id = users.id
             LEFT JOIN visits ON items.id = visits.item_id
             GROUP BY items.id
             ORDER BY items.id DESC"""
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT items.id, items.title, items.description, items.coordinates, 
                    items.created_date, users.id user_id, users.username
             FROM items
             JOIN users ON items.user_id = users.id
             WHERE items.id = ?"""
    result = db.query(sql, [item_id])
    return result[0] if result else None

def update_item(item_id, title, description, coordinates, loc_title, loc_value):
    sql = "UPDATE items SET title = ?, description = ?, coordinates = ? WHERE id = ?"
    db.execute(sql, [title, description, coordinates, item_id])

    sql = "DELETE FROM item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ?, ?)"
    db.execute(sql, [item_id, loc_title, loc_value])

def remove_item(item_id):
    sql = "DELETE FROM visits WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM images WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(search_query):
    sql = """SELECT DISTINCT items.id, items.title
             FROM items
             LEFT JOIN item_classes ON items.id = item_classes.item_id
             WHERE items.title LIKE ? OR items.description LIKE ? 
                OR item_classes.value LIKE ? OR item_classes.title LIKE ?
             ORDER BY items.id DESC"""
    like = "%" + search_query + "%"
    return db.query(sql, [like, like, like, like])
