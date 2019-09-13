#!/Users/fernando/workspace/IC/.virtualenv/bin/python2.7
# -*- coding: utf-8 -*-

# For resolve the macOSX bug - refer: https://markhneedham.com/blog/2018/05/04/python-runtime-error-osx-matplotlib-not-installed-as-framework-mac/
import pandas
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


order = pandas.read_csv('/Users/fernando/workspace/IC/SmartClassFogLB/v2/testes.csv')

df = pandas.read_json('/Users/fernando/workspace/IC/matplot/result/teste 1')
# pandas.DataFrame(df)
print(df)
print(df["times"])



meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
valores = [105235, 107697, 110256, 109236, 108859, 109986]

# /Users/fernando/workspace/IC/SmartClassFogLB/v2/testes.csv

plt.title('Faturamento no primeiro semestre de 2017')
plt.xlabel('Meses')
plt.ylabel('Faturamento em R$')
# plt.legend(loc='best')
plt.ylim(100000, 120000) # Definir os limites do eixo Y do gráfico

# plt.plot(meses, valores) # método plot criar gráficos de linha # plot(x, y)
plt.bar(meses, valores) # método plot criar gráficos de barras
# plt.pie(valores) # método plot criar gráficos de pizza

# plt.show()

# plt.savefig('nome_da_imagem.png', transparent = True) # export for image