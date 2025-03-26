preco = float(input("Preço: "))
desconto = preco * 0.07
aumento = preco * 0.055

preco_desconto = preco - desconto
preco_aumento = preco + aumento

print(f"Preço com desconto: {preco_desconto:.2f}")
print(f"Preço com aumento: {preco_aumento:.2f}")
