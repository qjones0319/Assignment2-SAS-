from flask import Flask, jsonify, request
import requests 

app = Flask(__name__)

user_shopping_cart = {}

myURL = "http://localhost:3000/products"

@app.route('/cart/<int:user_id>', methods=['GET'])  #Endpoint is used to get the cart contents
def get_cart(user_id):
    cart = user_shopping_cart.get(user_id, []) #Variable used to get the ID and the contents of the user
    cart_contents = { #Display the cart contents
        'cart': cart
    }
    return jsonify(cart_contents), 200 #Return the cart contents


#Endpoint is used to check if there is enough in stock to add to the cart, if there is enough in inventory, decrenent
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    
    
    quantity = request.json.get('quantity') #Retreive the quantity from the json request
    cart = user_shopping_cart.get(user_id, []) #Variable used to get the ID and the contents of the user
    response = requests.get(f'{myURL}/{product_id}') #Fetches the product from the product service
    
    #Check to see if the product inside the cart is in stock
    if response.status_code == 404:
        return jsonify({'error': 'Product not found'}), 404
    
    product = response.json() #Retreive the product from the product service
    product_update = product['product']['products_id'] #For updating product
    name_update = product['product']['name'] #For updating name
    prices_update = product['product']['prices'] #For updating prices
    updated_quantity = product['product']['quantity'] - quantity #For updating quantity
    
    
    #Check to see if there is enough in stock
    if product['product']['quantity'] < quantity:
        return jsonify({'error': 'Not enough in stock'}), 400
    
    updated_products = { #Dictionary to update the product
        "products_id": product_update,
        "name": name_update,
        "prices": prices_update,
        "quantity": updated_quantity
    }
    requests.post(f'{myURL}', json = updated_products) #Use json to update the product to my URL


    product_in_cart = None
    for item in cart: #To check the all the products in the cart
        if item['products_id'] == product_id:
            product_in_cart = item
            break

    if product_in_cart:
        product_in_cart["quantity"] += quantity #Increment the quantity for every quantity in the cart
        
    else:
        cart.append({ #Add all the updated products to the cart
            'products_id': product_id,
            'name': product['product']['name'],
            'prices': product['product']['prices'],
            'quantity': quantity         
        })

    user_shopping_cart[user_id] = cart #Save the updated cart to variable
    return jsonify({"cart": cart}), 200 #Return the updated cart

#Endpoint is removing the items that are already added in the cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST']) 
def remove_from_cart(user_id, product_id):
    quantity = request.json.get('quantity', 1) #Retreive the quantity from the json request
    cart = user_shopping_cart.get(user_id, []) #Variable used to get the ID and the contents of the user
    response = requests.get(f'{myURL}/{product_id}') #Fetches the product from the product service
    product_in_cart = next((item for item in cart if item['products_id'] == product_id), None) #Use list comprehension to find the product in the cart
    
    #Multiple if else statements are used to check if the product is in the cart, enough quantity in the cart for removal, and remove the product
    if not product_in_cart:
        return jsonify({'error': 'Product not in cart'}), 404
    
    product = response.json() #Retreive the product from the product service
    product_update = product['product']['products_id'] #For updating product
    name_update = product['product']['name'] #For updating name
    prices_update = product['product']['prices'] #For updating prices
    
    if product_in_cart['quantity'] < quantity:
        quantity = product_in_cart['quantity']
        cart.remove(product_in_cart)

    elif product_in_cart['quantity'] == quantity:
        cart.remove(product_in_cart)

    else:
        product_in_cart['quantity'] -= quantity #Decrement the quantity for every quantity in the cart

    updated_quantity = product['product']['quantity'] + quantity #For updating quantity
    #Check to see if the product inside the cart is in stock
    if response.status_code == 404:
        return jsonify({'error': 'Product not found'}), 404
    
    updated_products = { #Dictionary to update the product once the item has been removed
        "products_id": product_update,
        "name": name_update,
        "prices": prices_update,
        "quantity": updated_quantity    
    }
    requests.post(f'{myURL}', json = updated_products) #Use json to update the product to my URL
    user_shopping_cart[user_id] = cart #Save the updated cart to variable
    return jsonify({"cart": cart}), 200 #Return the updated cart

if __name__ == '__main__':
    app.run(debug=True, port = 4000)