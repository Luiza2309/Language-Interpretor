from sys import argv
from .Lexer import Lexer

def first_function(tokens):
	token = tokens.pop(0)

	while token[0] != "NUMBER":
		token = tokens.pop(0)
	
	first = token[1]

	while token[0] != "ENDEXPR":
		token = tokens.pop(0)

	return first

def sum_function(tokens):
	open_par = 1
	res = 0

	while 1:
		if tokens:
			token = tokens.pop(0)

			# firstly evaluate lambda and then make the sum
			if token[0] == "LAMBDA":
				output = []
				id = tokens.pop(0)[1]
				value = get_value(tokens)
				ids = [(id, value)]
				lambda_solver(tokens, output, id, value, ids, 0)
			
				# lambda returns a list and i add up the elements of the list
				while output:
					element = output.pop(0)
					res = res + element
				return res
			if token[0] == "STARTEXPR":
				open_par = open_par + 1

			if token[0] == "ENDEXPR":
				open_par = open_par - 1

			# it's the end of the sum expresion
			if open_par == 0:
				break

			# sum up the numbers
			if token[0] == "NUMBER":
				res += int(token[1])
		else:
			break
	
	return res

def append_function(tokens):
	open_par = 0
	res = []

	while 1:
		token = tokens.pop(0)
		if token[0] == "STARTEXPR":
			open_par = open_par + 1

		if token[0] == "ENDEXPR":
			open_par = open_par - 1

		# it's the end of the append expresion
		if open_par == 0:
			break

		if token[0] == "EMPTYLIST" and open_par > 1:
			res.append(())

		# append the numbers to the list
		if token[0] == "NUMBER":
			element = int(token[1])
			res.append(element)
	
	return res

# returns the value of a lambda id
# (lambda x: x 1) => x = 1
def get_value(tokens):
	open_par = 1
	value = []
	i = 0

	# jumps over the expression to get to the value
	while 1:
		if tokens[i][0] == "LAMBDA":
			i = i + 2
		if tokens[i][0] == "ENDEXPR":
			i = i + 1
			break
		if tokens[i][0] == "STARTEXPR":
			open_par_aux = 1
			i = i + 1

			while open_par_aux > 0:
				if tokens[i][0] == "STARTEXPR":
					open_par_aux = open_par_aux + 1
				elif tokens[i][0] == "ENDEXPR":
					open_par_aux = open_par_aux - 1

				i = i + 1
			
			break
		if tokens[i][0] == "ID":
			i = i + 1
			break

	# deletes the ")" at the end if there is one
	if i < len(tokens) and tokens[i][0] == "ENDEXPR":
		tokens.pop(i)

	# make the value
	while 1:
		token = tokens.pop(i)
		if token[0] == "STARTEXPR":
			open_par = open_par + 1

		if token[0] == "ENDEXPR":
			open_par = open_par - 1
		
		value.append(token)

		if open_par == 0:
			break

	# delete the ")" at the end if there is one
	if value[-1][0] == "ENDEXPR":
		value.pop(-1)

	return value

def lambda_solver(tokens, output, id, value, ids, nivel):	
	lambda_expresion = tokens.pop(0)

	if lambda_expresion[0] == "STARTEXPR":
		expr = [lambda_expresion]
		final_expr = []

		open_par = 1

		# compute the lambda expression
		# (lambda x: (x x) 1) => expr = (x x)
		first = False
		while open_par > 0:
			check = tokens.pop(0)
			if check[0] == "SUM" or check[0] == "APPEND":
				expr.append(check)
			if check[0] == "FIRST":
				first = True
				expr.append(check)
			if check[0] == "ID":
				expr.append(check)
			
			if check[0] == "STARTEXPR":
				open_par = open_par + 1
				expr.append(check)

			if check[0] == "ENDEXPR":
				open_par = open_par - 1
				expr.append(check)

		if len(value) == 1:
			value = value[0]

		# change the ids into their value
		# (lambda x: (x x) 1) => final_expr = (1 1)
		while expr:
			e = expr.pop(0)
			if e[0] != "ID":
				final_expr.append(e)
			else:
				for i in ids:
					if e[1] == i[0]:
						final_expr.extend(i[1])

		final_expr.extend(tokens)
		print(final_expr)

		# evaluate final expresion
		while final_expr:
			# if first:
			# 	final_expr = first_function(final_expr)
			# 	break
			# else:
			current_token = final_expr.pop(0)
			solve_current_token(current_token, final_expr, output, nivel + 1)

		output.extend(final_expr)
	if lambda_expresion[0] == "LAMBDA":
		id = tokens.pop(0)[1]
		value = get_value(tokens)

		new_ids = []
		seen_before = False
		for i in ids:
			if id == i[0]:
				new_ids.append((id, value))
				seen_before = True
			else:
				new_ids.append(i)

		if not seen_before:
			new_ids.append((id, value))

		ids.append((id, value))
		lambda_solver(tokens, output, id, value, new_ids, nivel)
		
	for i in ids:
		if lambda_expresion[1] == i[0]:
			if len(i[1]) == 1:
				output.append(i[1][0])
			elif i[1][0][0] == "LAMBDA":
				# evaluate the value further
				i[1].extend(tokens)
				while tokens:
					tokens.pop(0)
				current_token = i[1].pop(0)
				solve_current_token(current_token, i[1], output, nivel + 1)

def solve_current_token(current_token, tokens, output, nivel):
	if current_token[0] == "NUMBER" or current_token[0] == "EMPTYLIST":
		output.append(current_token[1])
	if current_token[0] == "STARTEXPR":
		check = tokens.pop(0)
		if check[0] == "NUMBER" or check[0] == "EMPTYLIST":

			# it's a list
			list_aux = []

			while check[0] != "ENDEXPR":			
				if check[0] == "STARTEXPR":
					solve_current_token(check, tokens, list_aux, nivel + 1)
				else:
					list_aux.append(check[1])
				check = tokens.pop(0)
			output.append(list_aux)
		elif check[0] == "SUM":
			# should compose the sum of the next list
			sum_res = sum_function(tokens)
			output.append(sum_res)
		elif check[0] == "APPEND":
			# should compose a list from multiple lists
			append_res = append_function(tokens)
			output.extend(append_res)
		elif check[0] == "FIRST":
			first_res = first_function(tokens)
			output.extend(first_res)
		elif check[0] == "LAMBDA":
			id = tokens.pop(0)[1]
			value = get_value(tokens)
			ids = [(id, value)]
			lambda_solver(tokens, output, id, value, ids, nivel)
		elif check[0] == "STARTEXPR":
			solve_current_token(check, tokens, output, nivel + 1)
		elif check[0] == "FIRST":
			first_res = first_function(tokens)
			output.extend(first_res)
	if current_token[0] == "LAMBDA":
		id = tokens.pop(0)[1]
		value = get_value(tokens)

		ids = [(id, value)]
		lambda_solver(tokens, output, id, value, ids, nivel)


def main():
	if len(argv) != 2:
		return
	
	# read from file
	filename = argv[1]
	f = open(filename, "r")
	input = f.read()

	# build lexer with specifications
	spec = [
		("NUMBER", "[0-9]+"),
		("EMPTYLIST", "\\(\\)"),
		("SUM", "\\+"),
		("APPEND", "\\+\\+"),
		("STARTEXPR", "\\("),
		("ENDEXPR", "\\)"),
		("FIRST", "first"),
		("LAMBDA", "lambda"),
		("ID", "([a-z] | [A-Z])+"),
		("STARTLAMBDA", ":"),
		("WHITESPACES", "(\n | \t | \\ )+")]
	l = Lexer(spec)

	tokens_aux = l.lex(input)
	tokens = []

	for token in tokens_aux:
		if token[0] != "WHITESPACES" and token[0] != "STARTLAMBDA":
			tokens.append(token)

	output = []

	current_token = tokens.pop(0)
	solve_current_token(current_token, tokens, output, 0)

	print(print_solution(output))

def print_solution(output, level = 0):
	if len(output) == 1 and level == 0:
		if isinstance(output[0], list):
			return print_solution(output[0], level + 1)
		if isinstance(output[0], tuple):
			return output[0][1]
		return str(output[0])

	ret = '( '
	for x in output:
		if isinstance(x, list):
			ret = ret + print_solution(x, level + 1) + ' '
		else:
			ret = ret + str(x) + ' '
	ret = ret + ')'

	return ret

if __name__ == '__main__':
    main()
