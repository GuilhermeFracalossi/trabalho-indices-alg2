from collections import deque
class TreeNode:
	def __init__(self, key, val):
		self.key = key
		self.val = val
		self.height = 1
		self.left = None
		self.right = None

class AVLTree:
	def _height(self, node):
		return node.height if node else 0
	
	def _update_height(self, node):
		if node:
			node.height = max(self._height(node.left), self._height(node.right)) + 1
	
	def _balance(self, node):
		return self._height(node.left) - self._height(node.right)
	
	def _left_rotate(self, x):
		y = x.right
		x.right = y.left
		y.left = x
		self._update_height(x)
		self._update_height(y)
		return y
	
	def _right_rotate(self, y):
		x = y.left
		y.left = x.right
		x.right = y
		self._update_height(y)
		self._update_height(x)
		return x
	
	def _balance_fix(self, node):
		balance = self._balance(node)
		if balance > 1:
			if self._balance(node.left) >= 0:
				return self._right_rotate(node)
			else:
				node.left = self._left_rotate(node.left)
				return self._right_rotate(node)
		if balance < -1:
			if self._balance(node.right) <= 0:
				return self._left_rotate(node)
			else:
				node.right = self._right_rotate(node.right)
				return self._left_rotate(node)
		return node
	
	def insert(self, node, key, val):
		if not node:
			return TreeNode(key, val)
		if key < node.key:
			node.left = self.insert(node.left, key, val)
		elif key > node.key:
			node.right = self.insert(node.right, key, val)
		else:
			node.val.append(val)  # assume valores duplicados são permitidos
		self._update_height(node)
		return self._balance_fix(node)
	def insert_value(self, node, key, val):
		existing_node = self.search(node, key)
		if existing_node:
			existing_node.val.append(val)  # adicionar a uma lista existente
			return node
		else:
			# armazenar o valor como uma lista
			return self.insert(node, key, [val])
	def search(self, node, key):
		# Esta função busca um nó com uma chave específica
		while node:
			if key < node.key:
				node = node.left
			elif key > node.key:
				node = node.right
			else:
				return node
		return None

	def print_tree(self, node, indent=0):
		if node:
			print(' ' * indent * 4, f'{node.key}({node.height})')
			if node.left or node.right:
				indent += 1
				if node.left:
					print(' ' * indent * 4 + 'L--', end='')
					self.print_tree(node.left, indent)
				if node.right:
					print(' ' * indent * 4 + 'R--', end='')
					self.print_tree(node.right, indent)


import pandas as pd
import re
def generateDataFile(path):
	global record_size
	df = pd.read_csv(path, delimiter=',')


	columns_to_keep = ['App Id', 'App Name', 'Category', 'Rating', 'Rating Count', 'Developer Id']
	# Mantenha apenas as colunas especificadas
	df = df[columns_to_keep]
	
	df['App Id'] = df['App Id'].str.strip()

	def check_non_latin(row):
		pattern = re.compile('[^a-zA-Z0-9,.\-_\s]+')
		row_str = ','.join([str(item) for item in row])
		return not bool(pattern.search(row_str))

	# Filtre as linhas contendo apenas caracteres permitidos
	df_filtered = df[df.apply(check_non_latin, axis=1)]

	df_sorted = df_filtered.sort_values(by=['App Id'], key=lambda x: x.str.lower())

	# Remova os índices antigos
	df_sorted = df_sorted.reset_index(drop=True)

	df_sorted.to_csv('datasetTeste.csv', index=False)

	def join_row(row):
		# Remove vírgulas extras dos valores antes de juntar
		cleaned_values = [str(value).replace(',', '').replace('"', '') for value in row]
		return ','.join(cleaned_values)

	joined_str_df = df_sorted.apply(join_row, axis=1)

	# Encontra o tamanho máximo
	max_length = joined_str_df.str.len().max()

	# Padroniza o tamanho dos registros adicionando espaços em branco
	padded_str_df = joined_str_df.str.pad(width=max_length, side='right')

	with open('sorted_data.bin', 'wb') as file:
		for record in padded_str_df:
			# Adiciona o caractere de nova linha ao final de cada registro e codifica para binário
			file.write((record + '\n').encode('utf-8'))


def create_index_campo1(file_path, field_index, frequency):
	data = {'index': [], 'App Id': []}
	line_counter = 0

	with open(file_path, 'rb') as file:
		while True:
			pos = file.tell()  # Pega a posição atual no arquivo antes de ler a linha
			line = file.readline().decode('utf-8').strip()

			if not line:
				break  # Fim do arquivo

			if line_counter % frequency == 0:  # Checa a frequência
				fields = line.split(',')
				field_value = fields[field_index]

				data['index'].append(pos)  # Adiciona a posição em vez do contador de índice
				data['App Id'].append(field_value)

			line_counter += 1

	df = pd.DataFrame(data)
	df.to_csv('index_campo1.csv', index=False)

import numpy as np
def create_index_campo2(file_path, field_index):
	data = {'index': [], 'App Name': []}

	with open(file_path, 'rb') as file:
		while True:
			pos = file.tell()
			line = file.readline().decode('utf-8').strip()

			if not line:
				break

			fields = line.split(',')
			app_name = fields[field_index]

			data['index'].append(pos)
			data['App Name'].append(app_name)

	df = pd.DataFrame(data)
	sorted_indices = np.argsort(df['App Name'].str.lower().values)
	df_sorted = df.iloc[sorted_indices].reset_index(drop=True)
	df_sorted.to_csv('index_campo2.csv', index=False)


import pandas as pd

def create_index_campo3(file_path):
	memory_index = {}
	with open(file_path, 'rb') as file:
		while True:
			pos = file.tell()  # Obtém a posição atual no arquivo
			line = file.readline().decode('utf-8').strip()
			if not line:
				break  # Fim do arquivo
			fields = line.split(',')
			field_value = fields[2]

			if field_value not in memory_index:
				memory_index[field_value] = []
			memory_index[field_value].append(pos)
	return memory_index

import math
def build_avl_tree_line_by_line(file_path):
	avl = AVLTree()
	root = None
	with open(file_path, 'rb') as file:
		while True:
			pos = file.tell()  # obtém a posição atual no arquivo
			line = file.readline().decode('utf-8', errors='ignore').strip()
			if not line:
				break  # Fim do arquivo
			fields = line.split(',')
			rating = fields[3]

			valor = float(rating)
			if math.isnan(valor):
				valor = 0

			root = avl.insert_value(root, valor, pos)
	#avl.print_tree(root)
	return root


def search_in_avl(root, value):
	positions = []
	print(root.key)
		
	if root is not None:
		if value < root.key:
			positions.extend(search_in_avl(root.left, value))
		elif value > root.key:
			positions.extend(search_in_avl(root.right, value))
		else:
			positions.extend(root.val)
	return positions

def fetch_records_from_positions(file_path, positions):
	records = []
	with open(file_path, 'rb') as file:
		for pos in positions:
			file.seek(pos)
			line = file.readline().decode('utf-8', errors='ignore').strip()
			records.append(line)
	return records

def main_query(file_path, query_value, root):
	positions = search_in_avl(root, query_value)
	records = fetch_records_from_positions(file_path, positions)
	return records


def binary_search(df, app_id):
	low = 0
	high = len(df) - 1
	closest = -1  # Valor mais próximo inicialmente não encontrado

	while low <= high:
		mid = (low + high) // 2
		mid_val = df.iloc[mid]['App Id'].lower()
		
		if mid_val < app_id:
			closest = df.iloc[mid]['index']
			low = mid + 1
		elif mid_val > app_id:
			#closest = df.iloc[mid]['index']
			high = mid - 1
		else:
			return df.iloc[mid]['index']  # Valor exato encontrado
	
	return closest


def search_by_app_id(index_csv, data_file_path, app_id):
	df = pd.read_csv(index_csv)
	
	app_id = app_id.lower().strip()
	closest_position = binary_search(df, app_id)

	if closest_position == -1:
		return "Binary search failed"
	
	with open(data_file_path, 'rb') as data_file:
		data_file.seek(closest_position)
		
		while True:
			line = data_file.readline().decode('utf-8').strip()

			if not line:
				return "Line not valid"
			
			fields = line.split(',')
			fields[0] = fields[0].lower().strip()
			if fields[0] == app_id:
				return line
			elif fields[0] > app_id:
				return "App Id not found"


def binary_search_app_name(df, target):
	low = 0
	high = len(df) - 1

	while low <= high:
		mid = (low + high) // 2
		mid_val = df.iloc[mid]['App Name'].lower().strip()

		
		if mid_val < target:
			low = mid + 1
		elif mid_val > target:
			high = mid - 1
		else:
			return df.iloc[mid]['index']

	return -1  # Não encontrado

def search_by_app_name(index_csv, data_file_path, target):
	df = pd.read_csv(index_csv)
	target = target.lower().strip()
	pos = binary_search_app_name(df, target)

	print(pos)
	if (pos == -1):
		return "Binary search not found"
	with open(data_file_path, 'rb') as data_file:
		data_file.seek(pos)
		line = data_file.readline().decode('utf-8').strip()

		if not line:
			return "Line invalid"
		fields = line.split(',')
		fields[1] = fields[1].lower().strip()
		if fields[1] == target:
			return line
		elif fields[1] > target:
			return "App Name not found"
		
def search_by_category(memory_index, file_path, search_value):
	if search_value not in memory_index:
		return "Value not found"

	positions = memory_index[search_value]
	records = []

	with open(file_path, 'rb') as file:
		for pos in positions:
			file.seek(pos)
			line = file.readline().decode('utf-8').strip()
			records.append(line)

	return records

def main ():
	GENERATE_DATA_FILE = False
	CREATE_FILE_INDEXES = True
	file_path = 'sorted_data.bin'
	if GENERATE_DATA_FILE:
		generateDataFile('Google-Playstore.csv')

	if CREATE_FILE_INDEXES:
		create_index_campo1(file_path, 0, 100)
		create_index_campo2(file_path, 1)

	memory_index = create_index_campo3(file_path)
	rootAvl = build_avl_tree_line_by_line(file_path)

	while True:
		print("Escolha uma opção de consulta:")
		print("1: Consultar por App ID")
		print("2: Consultar por Nome")
		print("3: Consultar por Categoria")
		print("4: Consultar por Rating")
		print("5: Sair")
		
		choice = input("Digite sua escolha: ")

		if choice == '1':
			app_id = input("Digite o App ID: ")
			result = search_by_app_id('index_campo1.csv', file_path, app_id)
			print(result)
			print()
		elif choice == '2':
			app_name = input("Digite o nome do aplicativo: ")
			result = search_by_app_name('index_campo2.csv', file_path, app_name)
			print(result)
			print()
		elif choice == '3':
			category = input("Digite a categoria: ")
			result = search_by_category(memory_index, file_path, category)
			if result:
				formatted_result = "\n".join([str(record) for record in result])
				print(f"Resultado(s):\n{formatted_result}")
			else:
				print("Nenhum resultado encontrado.")
		elif choice == '4':
			rating = float(input("Digite o rating: "))
			result = main_query(file_path, rating, rootAvl)
			if result:
				formatted_result = "\n".join([str(record) for record in result])
				print(f"Resultado(s):\n{formatted_result}")
			else:
				print("Nenhum resultado encontrado.")
		elif choice == '5':
			print("Saindo...")
			break
		else:
			print("Escolha inválida.")
			continue


main()
