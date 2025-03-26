# Professor pediu para fazer esse programa de calcular média de 3 notas que vão de 0 a 10.

n1 = float(input("Nota 1 (0 a 10): "))
while n1 < 0 or n1 > 10:
    n1 = float(input("Nota 1 (0 a 10): "))

n2 = float(input("Nota 2 (0 a 10): "))
while n2 < 0 or n2 > 10:
    n2 = float(input("Nota 2 (0 a 10): "))

n3 = float(input("Nota 3 (0 a 10): "))
while n3 < 0 or n3 > 10:
    n3 = float(input("Nota 3 (0 a 10): "))

soma = n1 + n2 + n3
resultado = soma / 3

print(f"{resultado:.2f}")
