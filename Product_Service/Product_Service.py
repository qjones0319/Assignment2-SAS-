from flask import Flask, jsonify, request
app = Flask(__name__)

add_products = {}

# Endpoint 1: Get all the products 
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify({"products": add_products})

# Endpoint 2: Get a specific product by ID 
@app.route('/products/<int:products_id>', methods=['GET'])
def get_product_id(products_id):
    product = add_products.get(products_id)
    if product:
        return jsonify({"product": product})
    else:
        return jsonify({"error": "Product not found"}), 404

# Endpoint 3: Create new produts 
@app.route('/products', methods=['POST'])
def adding_products():    
    item_information = request.json
    add = len(add_products) + 1
    products_id = item_information.get('products_id', add)
    name_information = item_information.get('name')
    price_information = item_information.get('prices')
    quantity_information = item_information.get('quantity')
    new_product = {
        "products_id": products_id,
        "name" : name_information,
        "prices": price_information,
        "quantity": quantity_information
    }
    add_products[products_id] = new_product
    return jsonify({"message": "Product created", "product": new_product}), 201

if __name__ == '__main__':
    app.run(debug=True, port = 3000)
