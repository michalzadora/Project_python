# import standard library re with Regex for easier string service
from re import sub, findall
from collections import OrderedDict

negation = "!"
operators = "|&>=^"


# Small functions

def count_char(input):
    counter = 0
    for char in input:
        if char == "-":
            counter = counter + 1
    return counter


def count_true(expr):
    counter = 0
    for i in expr:
        if i == "1":
            counter += 1
    return counter


def compare_and_combine(param1, param2):
    differences = 0
    combination = ""
    if param1 and param2:
        for bit in range(len(param1)):
            if param1[bit] != param2[bit]:
                differences += 1
                combination += "-"
            else:
                combination += param2[bit]
        if differences > 1:
            return ""
        else:
            return combination
    else:
        return ""


def get_connector_index(expr):
    connector = expr.find(">")
    if connector < 0:
        connector = expr.find("=")
    return connector


def take_right_part(expr):
    connector = get_connector_index(expr)
    if connector < 0:
        return ""
    return expr[connector + 1:]


def take_left_part(expr):
    connector = get_connector_index(expr)
    if connector < 0:
        return ""
    return expr[:connector]


def change_variables(expr):
    new_expr = sub(r'\w+', 'm', expr)
    return new_expr


def make_variables(expr):
    variables = findall(r'[A-Za-z_]\w*', expr)
    # we dont wanna duplicates so first we do OrderDict and next list of variables
    return list(OrderedDict.fromkeys(variables))


def decimal_bin(decimal, length):
    if length < 1:
        return ""
    binary = bin(decimal)
    binary = binary[2:]
    return "0" * (length - len(binary)) + binary


def get_result(parts):
    res = ""
    for part in parts:
        res = res + " + " + part
    return res[3:]


# ====================================================================
# Validation of expression and eval of operators.

# It's part that we prepare on laboratory, with a few differences:
def validate(expr):
    state = 0
    parentheses_counter = 0
    new_expr = change_variables(expr)
    for char in new_expr:
        if char == " ":
            continue
        if state == 0:
            if char == 'm':
                state = 1
            elif char == "(":
                parentheses_counter += 1
            elif char in negation:
                state = 0
            else:
                return False
        elif state == 1:
            if char in operators:
                state = 0
            elif char == ")":
                parentheses_counter -= 1
            else:
                return False
        if parentheses_counter < 0:
            return False
    if state == 1 and parentheses_counter == 0:
        return True
    else:
        return False


def negate(operand):
    if operand == "1":
        return "0"
    else:
        return "1"


def use_operators(operator, left, right):
    if operator == "&":
        if right == "1" and left == "1":
            return "1"
        else:
            return "0"
    elif operator == "|":
        if left == "1" or right == "1":
            return "1"
        else:
            return "0"
    elif operator == "^":
        if (left == "1" and right == "0") or (left == "0" and right == "1"):
            return "1"
        else:
            return "0"
    elif operator == "=":
        if (left == "0" and right == "0") or (left == "1" and right == "1"):
            return "1"
        else:
            return "0"
    elif operator == ">":
        if left == "1" and right == "0":
            return "0"
        else:
            return "1"


def evaluate(expr, variables, binaries):
    copy_expr = expr
    for i in range(0, len(binaries)):
        copy_expr = sub("(?<!\w)" + variables[i] + "(?!\w)", binaries[i], copy_expr)
    # Using two stacks for simplify job
    stack_arguments = []
    stack_operators = []
    for value in copy_expr:
        if value == "0" or value == "1":
            stack_arguments.append(value)
        elif value == "(":
            stack_operators.append(value)
        elif value in negation:
            stack_operators.append(value)
        elif value in operators:
            while stack_operators:
                # in order of priorities operators
                if stack_operators[-1] in negation:
                    argument = stack_arguments.pop()
                    stack_operators.pop()
                    stack_arguments.append(negate(argument))
                elif stack_operators[-1] == "&":
                    operator = stack_operators.pop()
                    right_arg = stack_arguments.pop()
                    left_arg = stack_arguments.pop()
                    stack_arguments.append(use_operators(operator, left_arg, right_arg))
                else:
                    break
            stack_operators.append(value)
        elif value == ")":
            while stack_operators[-1] != "(" and stack_operators:
                operator = stack_operators.pop()
                if operator in negation:
                    stack_arguments.append(negate(stack_arguments.pop()))
                elif operator in operators:
                    right_arg = stack_arguments.pop()
                    left_arg = stack_arguments.pop()
                    stack_arguments.append(use_operators(operator, left_arg, right_arg))
            stack_operators.pop()
    while stack_operators:
        operator = stack_operators.pop()
        if operator in negation:
            stack_arguments.append(negate(stack_arguments.pop()))
        elif operator in operators:
            right_arg = stack_arguments.pop()
            left_arg = stack_arguments.pop()
            stack_arguments.append(use_operators(operator, left_arg, right_arg))
    return stack_arguments.pop()


def generate_true_list(expr):
    variables = make_variables(expr)
    length = len(variables)
    res = []
    for i in range(0, 2 ** length):
        binaries = decimal_bin(i, length)
        if evaluate(expr, variables, binaries) == "1":
            res.append(binaries)
    return res


def group_together(list_groups):
    flag = False
    comp_list = []
    checked_list = []
    length = len(list_groups)
    for i in range(length):
        comp_list.append([])
        checked_list.append([])
        for j in range(len(list_groups[i])):
            checked_list[i].append(False)
    for i in range(length - 1):
        for j in range(len(list_groups[i])):
            for item2_index in range(len(list_groups[i + 1])):
                success = compare_and_combine(list_groups[i][j], list_groups[i + 1][item2_index])
                if success:
                    comp_list[count_true(success)].append(success)
                    checked_list[i][j] = True
                    checked_list[i + 1][item2_index] = True
                    flag = True
    for i in range(length):
        for j in range(len(list_groups[i])):
            if (checked_list[i][j] == False):
                comp_list[count_true(list_groups[i][j])].append(
                    list_groups[i][j])
    list_groups = comp_list
    for i in range(length):
        list_groups[i] = list(OrderedDict.fromkeys(list_groups[i]))
    if flag:
        list_groups = group_together(list_groups)
    return list_groups


#
# def group_together(list_groups):
#     length = len(list_groups)
#     # Checked group is for marking used groups
#     checked_group = []
#     comb_group = []
#     for i in range(length):
#         comb_group.append([])
#     for i in range(length):
#         checked_group.append([])
#         for k in range(len(list_groups[i])):
#             checked_group[i].append(False)
#     # Now we have to combine next groups together from group 0 to len -1
#     # because last one dont have next group :)
#     flag = False
#     for i in range(length - 1):
#         # We need to check all permutations.
#         for j in range(len(list_groups[i])):
#             for k in range(len(list_groups[i + 1])):
#                 success = compare_and_combine(list_groups[i][j], list_groups[i + 1][k])
#                 if success:
#                     flag = True
#                     checked_group[i][j] = True
#                     checked_group[i + 1][k] = True
#                     comb_group[count_true(success)].append(success)
#     for i in range(length):
#         for index in range(len(list_groups[i])):
#             if checked_group[i][index] == False:
#                 comb_group[count_true(list_groups[i][index])].append(list_groups[i][index])
#     for i in range(length):
#         list_groups[i] = list(OrderedDict.fromkeys(list_groups[i]))
#     if flag:
#         list_groups = group_together(list_groups)
#     return list_groups


def make_binaries(input):
    binaries = [input]
    while len(binaries) != 2 ** count_char(input) and binaries:
        for i in range(len(binaries[0])):
            if binaries[0][i] == "-":
                binaries.append(binaries[0][:i] + "0" + binaries[0][i + 1:])
                binaries.append(binaries[0][:i] + "1" + binaries[0][i + 1:])
                binaries.remove(binaries[0])
                break
    return binaries


def make_chart(flatten_list, list_ones):
    len_flatten = len(flatten_list)
    len_ones = len(list_ones)
    prime_chart = []
    for i in range(len_flatten):
        prime_chart.append([])
        for j in range(len_ones):
            prime_chart[i].append(0)

    for i in range(len_flatten):
        for binary in make_binaries(flatten_list[i]):
            for index in range(len_ones):
                if list_ones[index] == binary:
                    prime_chart[i][index] = 1
    return prime_chart


def generate_part_result(variables, param):
    res = ""
    for i in range(0, len(variables)):
        if param[i] == "0":
            res = res + " " + variables[i] + "'"
        elif param[i] == "1":
            res = res + " " + variables[i]
    return res[1:]


# Essentail prime when we have only one expr in row
def eliminate_essential(prime_chart, variables, flatten_list):
    result = []
    # y is column, x is row
    for y in range(len(prime_chart[0])):
        counter = 0
        for x in range(len(prime_chart)):
            if prime_chart[x][y] == 1:
                counter = counter + 1
                finded_row = x
        if counter == 1:
            result.append(generate_part_result(variables, flatten_list[finded_row]))
            # Mark covered columns
            for y in range(len(prime_chart[0])):
                if prime_chart[finded_row][y] == 1:
                    for x in range(len(prime_chart)):
                        prime_chart[x][y] = 0
    return list(OrderedDict.fromkeys(result))


def check_prime_chart(prime_chart, x, y):
    for row in range(x):
        for column in range(y):
            if prime_chart[row][column] != 0:
                return False
    return True


# we have to gather rest factors and minimalize them because they can be multiplied
def gather_factor(first, second):
    if first == [] and second == []:
        return []
    if first == []:
        return second
    if second == []:
        return first
    combination = []
    for i in first:
        for j in second:
            if i != j:
                combination.append(list(OrderedDict.fromkeys(i + j)))
            else:
                combination.append(j)
    return combination


def count_cost(param):
    cost = 0
    for char in param:
        if char != "-":
            cost = cost + 1
    return cost


def petrick_method(prime_chart, variables, flatten_list):
    the_rest = []
    for y in range(len(prime_chart[0])):
        part_rest = []
        for x in range(prime_chart):
            if prime_chart[x][y] == 1:
                part_rest.append([x])
        if part_rest:
            the_rest.append(part_rest)
    for current in range(len(the_rest) - 1):
        the_rest[current + 1] = gather_factor(the_rest[current], the_rest[current + 1])
    gathered = the_rest[-1]
    gathered = sorted(gathered, key=len)
    length = len(gathered[0])
    temp = []
    for i in gathered:
        if length == len(i):
            temp.append(i)
    costs = []
    for tmp in temp:
        cost = 0
        for i in range(len(flatten_list)):
            for index in tmp:
                cost = cost + count_cost(flatten_list[index])
        costs.append(cost)
    min_costs = []
    for j in range(len(costs)):
        if min(costs) == costs[j]:
            min_costs.append(temp[j])
    result = []
    for i in min_costs[0]:
        result.append(generate_part_result(variables, flatten_list[i]))
    return result


def quine_mccluskey(expr, variables, list_ones):
    # Begining condition
    if len(list_ones) == 2 ** len(variables):
        return "1"
    if len(list_ones) == 0:
        return "0"
    # Start from making structs for grouping
    list_groups = []
    for i in range(len(list_ones[0]) + 1):
        list_groups.append([])
    for one in list_ones:
        list_groups[count_true(one)].append(one)
    # Let's begin group together
    list_groups = group_together(list_groups)
    flatten_list = []
    for i in list_groups:
        for j in i:
            flatten_list.append(j)
    # Now we can prepare to use Petrick's method
    # https://www.allaboutcircuits.com/technical-articles/prime-implicant-simplification-using-petricks-method/
    prime_chart = make_chart(flatten_list, list_ones)
    prime_essential = eliminate_essential(prime_chart, variables, flatten_list)
    if check_prime_chart(prime_chart, len(flatten_list), len(list_ones)):
        # If we have 0 in every row and column we are done but if not we have to add rest of
        return get_result(prime_essential)
    else:
        return get_result(prime_essential) + " + " + get_result(petrick_method(prime_chart, variables, flatten_list))


def algorithm(expr):
    if validate(expr):
        print("Mimimalization result: " + quine_mccluskey(expr, make_variables(expr), generate_true_list(expr)))
    else:
        print("Something wrong with exprression (it's invalid).")


def main():
    expr = input("Expr: ")
    algorithm(expr)


if __name__ == "__main__":
    main()
