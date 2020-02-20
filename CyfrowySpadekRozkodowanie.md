# Cyfrowy Spadek, rozszyfrowanie:

1. Skompletuj wszystkie linie zaszyfrowanego hasła.
1. Każda z linii zaszyfrowanego hasła reprezentuje osobny ciąg binarny zakodowany szesnastkowo. 
    (Każdy znak zapisu szesnastkowego odpowiada dokładnie czterem bitom ciągu binarnego). 
    Weź dwie (dowolne) linie zaszyfrowanego hasła i wykonaj logiczną operację XOR na tych dwóch ciągach binarnych. 
    (Czyli: wykonaj operację na każdej parze bitów będących na tych samych kolejnych pozycjach w obu ciągach i zapisz rezultat w formie ciągu wynikowego.)
3. Weź następną (dowolną ale dotąd niewykorzystaną) linię zaszyfrowanego hasła i wykonaj logiczną operację XOR na tym ciągu binarnym 
    i na ciągu będącym rezultatem poprzedniej operacji.
4. Powtarzaj krok opisany powyżej aż do wyczerpania wszstkich linii zaszyfrowanego hasła.
5. Każdy bajt (8-bitów) wynikowego ciągu binarnego reprezentuje jeden znak hasła przedstawiony w kodowaniu UTF-8 (ASCII). 
  Oblicz wartość numeryczną każdego kolejnego bajtu i znajdź odpowiadające tym wartościom znaki w tabeli kodu ASCII.
6. Użyj programu [VeraCrypt](http://www.veracrypt.fr) wraz z rozkodowanym powyżej hasłem aby zamontować na swoim komputerze 
     posiadany zaszyfrowany nośnik danych jako dysk wirtualny. 
     Plik README.txt w katalogu głównym tego dysku wirtualnego zawiera dalsze informacje.

----

Kroki od 2 do 5 włącznie w powyższej procedurze mogą być realizowane programowo.    

Przykładowy program deszyfrujący napisany w Pythonie jest następujący:

```python
#!/usr/bin/python3

lst = [bytes.fromhex(x) for x in input().split()]
out_bytes = lst[0]
for pad_bytes in lst[1:]:
    out_bytes = [(a ^ b) for a,b in zip(out_bytes, pad_bytes)]
print(''.join([chr(x) for x in out_bytes]))
```

Program ten znajduje się także [w tym repozytorium](https://github.com/rogowskz/one-time-pad) w pliku: `src/main/pyton/one-time-pad-minimal-decryptor-py3.py`    
    
JEŚLI Wszystkie linie zaszyfrowanego hasła są zapisane w pliku tekstowym: `ciphertext.txt`    
ORAZ Program `one-time-pad-minimal-decryptor-py3.py` znajduje się w tym samym katalogu co plik `ciphertext.txt`    
TO Komenda rozszyfrowująca hasło (w konsoli powłoki Bash) jest następująca:

```bash
cat ciphertext.txt | tr '\n' ' ' | python3 one-time-pad-minimal-decryptor-py3.py
```

