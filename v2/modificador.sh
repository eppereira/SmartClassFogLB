#!/bin/bash
for f in result/*; do
	
	#add chaves no inicio e fim do arquivo
	file=$(echo $f | cut -d'/' -f 2)_mod	
	echo $file
	echo "[" > $file
	cat $f >> $file
	echo "]" >> $file

	#add virgula entre os colchetes
	sed -i 's/}{/},{/g' $file

done
echo 'Concluído'
