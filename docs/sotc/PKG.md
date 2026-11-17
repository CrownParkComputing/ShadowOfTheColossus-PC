# Instalar um PKG local

O instalador aceita um PKG de desenvolvimento/fake-PKG legivel com as chaves publicas
desse formato. PKGs de varejo que exigem chaves do console nao sao suportados.
Nenhum jogo, DLC ou firmware e incluido no port.

No Linux, compile com `bash build.sh` e instale:

```bash
python3 sotc.py --install-pkg "/caminho/jogo.pkg" --out ../CUSA08034
SOTC_GAME_DIR=../CUSA08034 BB_PREBUILT=1 bash run.sh
```

No pacote Windows:

```bat
SotC.exe --run --install-pkg "D:\jogo.pkg" --out "D:\CUSA08034"
```

Escolha uma pasta nova para a instalacao. O destino deve ter espaco para os arquivos
extraidos; a pasta pai tambem precisa de espaco temporario equivalente ao PKG.
Os dados sao lidos em blocos, sem carregar o jogo inteiro na RAM. O auxiliar
`sotc-pkgdec` (`.exe` no Windows) e encontrado em `bin/` ou `out/`.

Depois, configure `SOTC_GAME_DIR` no `sotc.ini` com a pasta que contem `eboot.bin`.
Para os DLCs de direito de acesso do SotC, `SOTC_DLC_DIR` pode apontar para uma pasta
com os PKGs de add-on da mesma regiao; eles nao precisam ser extraidos. Um DLC com
dados adicionais nao e montado por esse mecanismo.
