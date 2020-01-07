# Cyfrowy Spadek, rozkodowanie:

1. Skompletuj wszystkie linie zaszyfrowanego hasła.
1. Każda z linii zaszyfrowanego hasła reprezentuje osobny ciąg binarny zakodowany szesnastkowo. Weź dwie (dowolne) linie 
    zaszyfrowanego hasła i wykonaj logiczną operację XOR na tych dwóch ciągach binarnych. 
    (Czyli: wykonaj operację na każdej parze bitów będących na tych samych kolejnych pozycjach w obu ciągach i zapisz rezultat w formie ciągu wynikowego.)
1. Weź następną (dowolną ale dotąd niewykorzystaną) linię zaszyfrowanego hasła i wykonaj logiczną operację XOR na tym ciągu binarnym 
    i na ciągu będącym rezultatem poprzedniej operacji.
1. Powtarzaj krok opisany powyżej aż do wyczerpania wszstkich linii zaszyfrowanego hasła.
1. Każdy bajt (8-bitów) wynikowego ciągu binarnego reprezentuje jeden znak hasła przedstawiony w kodowaniu UTF-8 (ASCII). 
  Oblicz wartość numeryczną każdego kolejnego bajtu i znajdź odpowiadające tym wartościom znaki w tabeli kodu ASCII.
1. Użyj programu [VeraCrypt](http://www.veracrypt.fr) wraz z rozkodowanym powyżej hasłem aby zamontować na swoim komputerze 
     posiadany zaszyfrowany nośnik danych jako dysk wirtualny. 
     Plik README.txt w katalogu głównym tego dysku wirtualnego zawiera dalsze informacje.
