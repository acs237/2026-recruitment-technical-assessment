from dataclasses import dataclass
from typing import Any, List, Dict, Union
from flask import Flask, request, jsonify
import re
import json

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int

# file to store the cookbook
COOKBOOK_FILE = 'cookbook.json'

# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Retrieve the cookbook from the file
def get_cookbook():
	# Retrieve the cookbook from the file
	try:
		with open(COOKBOOK_FILE, 'r') as cookbook_file:
			cookbook = [json.loads(line) for line in cookbook_file]
	except FileNotFoundError:
		cookbook = []
	return cookbook

# Store the cookbook to the file
def store_cookbook(data):
	with open(COOKBOOK_FILE, 'a') as cookbook_file:
		cookbook_file.write(json.dumps(data) + '\n')

# look for the item in the cookbook
def look_for_item(name: str, cookbook: List[Dict[str, Any]]) -> Dict[str, Any] | None:
	for item in cookbook:
		if item['name'] == name:
			return item
	return None

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	# replacing hyphens and underscores with whitespace
	recipeName = re.sub(r'[-_]', ' ', recipeName)

	# contain only letter and whitespaces
	recipeName = re.sub(r'[^a-zA-Z\s]', '', recipeName)

	# capitalise the first letter of each word
	recipeName = recipeName.title()

	# only one whitespace between words, remove leading and trailing whitespace
	recipeName = re.sub(r'\s+', ' ', recipeName)
	recipeName = recipeName.strip()

	# if the string is empty, return None
	if len(recipeName) == 0:
		return None

	return recipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	# TODO: implement me

	# get the cookbook
	cookbook = get_cookbook()

	# get the data from the request
	data = request.get_json()

	# check the conditions
	# type can only be 'recipe' or 'ingredient'
	if data['type'] not in ['recipe', 'ingredient']:
		return jsonify({'error': 'Invalid type'}), 400

	# cookTime can only be greater than or equal to 0
	if data['type'] == 'ingredient' and data['cookTime'] < 0:
		return jsonify({'error': 'Invalid cookTime'}), 400

	# entry names must be unique
	is_present = any(d.get('name') == data['name'] for d in cookbook)
	if is_present:
		return jsonify({'error': 'Name already exists'}), 400

	# recipe requiredItems can only have one element per name
	if data['type'] == 'recipe':
		required_items = data['requiredItems']
		unique_names = set[str](item['name'] for item in required_items)
		if len(unique_names) != len(required_items):
			return jsonify({'error': 'Required items must have unique names'}), 400

	# write the data to the cookbook
	store_cookbook(data)
	return jsonify({}), 200

# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	'''
		read the recipe from the json file one time to avoid multiple reads
		'ingredients' is a dictionary so that can simply loop through the dictionary to output summary
		using queue for searching ingredients one level down after another
		
	'''
	# get the name from the query parameters
	name = request.args.get('name')

	# get the cookbook
	cookbook = get_cookbook()

	# check if the name is in the cookbook
	target = look_for_item(name, cookbook)
	if target is None or target['type'] != 'recipe':
		return jsonify({'error': 'Recipe not found'}), 400

	# initialize the cooktime and ingredients
	total_cooktime = 0
	
	ingredients = {}
	ingredients[target['name']] = {
		'quantity': 1,
		'unit_cook_time': 0
	}

	# get the ingredients recursively
	queue = [target['name']]
	while queue:
		current = queue.pop(0)
		# look for the item in the cookbook
		current_item = look_for_item(current, cookbook)
		if current_item is None:
			return jsonify({'error': 'Items not in the cookbook'}), 400

		# if the current item is a recipe
		# add the "requiredItems" to the queue
		if current_item['type'] == 'recipe':
			# remove the current item from the ingredients list
			popped_item =ingredients.pop(current_item['name'], None)
			popped_item_quantity = 0
			if popped_item is not None:
				popped_item_quantity = popped_item['quantity']

			# loop through required items
			# add names to the queue
			# add name, quantity, and cook time (initially as 0) to the ingredients list
			for item in current_item['requiredItems']:
				queue.append(item['name'])

				# check if the item is already in the ingredients list
				if item['name'] in ingredients:
					ingredients[item['name']]['quantity'] += popped_item_quantity * item['quantity']
				else:
					ingredients[item['name']] = {
						'quantity': popped_item_quantity * item['quantity'],
						'unit_cook_time': 0
					}
		
		# if the current item is an ingredient
		if current_item['type'] == 'ingredient':
			# add the cook time to the ingredients list
			ingredients[current_item['name']]['unit_cook_time'] = current_item['cookTime']

	# loop through the ingredients list to calculate the total cook time
	for item in ingredients:
		total_cooktime += ingredients[item]['quantity'] * ingredients[item]['unit_cook_time']

	# get the ingredients list [{name, quantity}]
	ingredients_list = [{'name': item, 'quantity': ingredients[item]['quantity']} for item in ingredients]
	
	return jsonify({
		'name': name,
		'cookTime': total_cooktime,
		'ingredients': ingredients_list
	}), 200


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
