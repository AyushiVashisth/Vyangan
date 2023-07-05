from flask import Flask, render_template, request, redirect, flash
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load data from db.json
with open('db.json', 'r') as f:
    data = json.load(f)

menu = data['menu']
orders = data['orders']

# Routes and views
@app.route('/')
def home():
    return redirect('/menu')

@app.route('/menu')
def show_menu():
    return render_template('menu.html', menu=menu)

@app.route('/add_dish', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        dish_id = int(request.form['dish_id'])
        dish_name = request.form['dish_name']
        price = float(request.form['price'])
        availability = True if request.form.getlist('availability') else False
        quantity = int(request.form['quantity'])

        menu.append({"dish_id": dish_id, "dish_name": dish_name, "price": price, "availability": availability, "quantity": quantity})
        flash(f"Dish '{dish_name}' added successfully!")

        # Save data to db.json
        save_data()

        return redirect('/menu')
    return render_template('add_dish.html')


@app.route('/remove_dish', methods=['GET', 'POST'])
def remove_dish():
    if request.method == 'POST':
        dish_id = int(request.form['dish_id'])
        dish_name = None
        for dish in menu:
            if dish['dish_id'] == dish_id:
                dish_name = dish['dish_name']
                menu.remove(dish)
                flash(f"Dish '{dish_name}' removed successfully!")
                break
        if dish_name is None:
            flash(f"Dish with ID {dish_id} does not exist!")

        # Adjust dish IDs after removal
        for index, dish in enumerate(menu):
            dish['dish_id'] = index + 1

        # Save data to db.json
        save_data()

        return redirect('/menu')
    return render_template('remove_dish.html')


@app.route('/update_availability', methods=['GET', 'POST'])
def update_availability():
    if request.method == 'POST':
        dish_id = int(request.form['dish_id'])
        availability = True if request.form.getlist('availability') else False

        for dish in menu:
            if dish['dish_id'] == dish_id:
                dish['availability'] = availability
                flash(f"Availability of dish '{dish['dish_name']}' updated!")
                break

        # Save data to db.json
        save_data()

        return redirect('/menu')
    return render_template('update_availability.html')

@app.route('/order', methods=['GET', 'POST'])
def take_order():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        order_dish_ids = request.form['dish_ids'].split(",")
        ordered_dishes = []
        total_price = 0

        for dish_id in order_dish_ids:
            dish_id = int(dish_id.strip())
            for dish in menu:
                if dish['dish_id'] == dish_id and dish['availability'] and dish['quantity'] > 0:
                    ordered_dishes.append(dish['dish_name'])
                    total_price += dish['price']
                    dish['quantity'] -= 1
                    break

        if ordered_dishes:
            order_id = len(orders) + 1
            order = {"order_id": order_id, "customer_name": customer_name, "dishes": ordered_dishes, "status": "Pending"}
            orders.append(order)
            flash(f"Order placed successfully! Order ID: {order_id}")
        else:
            flash("No dishes available for order!")

        # Save data to db.json
        save_data()

        # Redirect to /orders to see the updated orders list
        return redirect('/orders')

    return render_template('order.html', menu=menu)




@app.route('/orders')
def view_orders():
    return render_template('orders.html', orders=orders)

@app.route('/update_status', methods=['GET', 'POST'])
def update_order_status():
    if request.method == 'POST':
        order_id = int(request.form['order_id'])
        status = request.form['status']

        for order in orders:
            if order['order_id'] == order_id:
                order['status'] = status
                flash(f"Order ID {order_id} status updated to {status}")
                break
        else:
            flash(f"Order ID {order_id} not found!")

        # Save data to db.json
        save_data()

        return redirect('/orders')

    return render_template('update_status.html', orders=orders)

def save_data():
    data = {"menu": menu, "orders": orders}
    with open('db.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    app.run(debug=True)
