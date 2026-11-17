# Fork CrownParkComputing

Este repositorio e um fork de
[AjncSystem/ShadowOfTheColossus-PC](https://github.com/AjncSystem/ShadowOfTheColossus-PC).
Base das mudancas locais: `4601325`, release upstream 0.76.1. Nao e uma
reescrita independente, nem um lancamento oficial do upstream. O historico,
os creditos e a licenca GPL do projeto sao preservados.

## Dependencias upstream

- O runtime e a infraestrutura derivam de
  [Supermedo/bloodborne_pc](https://github.com/Supermedo/bloodborne_pc).
- O video core shadPS4 e incluido como fonte, nao como submodulo. A origem, o
  commit e os backports estao em [`gpu/VENDOR.txt`](../../gpu/VENDOR.txt);
  a licenca fica em `gpu/shadps4/LICENSE`.
- `.gitmodules` declara FSR-Vulkan, ImGui, LibAtrac9, magic_enum, miniz e Xbyak.
  Cada dependencia fica fixada pelo gitlink do repositorio, nao pela ponta de
  uma branch. As licencas originais permanecem nas dependencias.
- FSR-Vulkan continua no upstream FireBurn, commit
  `c64f093404125e960813f95f1996c14780f0dd69`. As duas alteracoes do port ja estao
  em `gpu/patches/fsr-vulkan/` e sao aplicadas pelo build de forma idempotente.
  Por isso esse submodulo pode aparecer modificado depois de compilar.
- As constantes publicas do formato fake-PKG em `scripts/pkg_extract.py` vem de
  [Antti/orbis](https://github.com/Antti/orbis), arquivo `orbis-pkg/src/keys.rs`,
  verificadas no commit `acf5f5d64cd5095fd6227cafe995863c7750b833`.
  Sao usadas sob a opcao MIT; o aviso integral esta em
  [`third_party/licenses/orbis-MIT.txt`](../../third_party/licenses/orbis-MIT.txt).
  Nao sao chaves pessoais ou extraidas do console do usuario.

## Clonar e compilar no Linux

```bash
git clone --recurse-submodules https://github.com/CrownParkComputing/ShadowOfTheColossus-PC.git
cd ShadowOfTheColossus-PC
git remote add upstream https://github.com/AjncSystem/ShadowOfTheColossus-PC.git
bash build.sh
cp sotc.ini.example sotc.ini
SOTC_GAME_DIR=/caminho/para/seu/dump BB_PREBUILT=1 bash run.sh
```

Use toolchain x86-64 com C++23 e as dependencias listadas em `shell.nix`.
Em Nix, `nix-shell --run 'bash build.sh'` fornece o ambiente. Em outras
distribuicoes instale os equivalentes (Vulkan, SDL3, FFmpeg e bibliotecas de
desenvolvimento listadas no arquivo). O comando `build-linux.sh` do upstream
e para compilacao cruzada Windows, nao para executar o port nativamente.

O exemplo de configuracao desliga a captura do mouse, ativa a leitura
antecipada de arquivos quando a RAM permite e termina os pipelines em cache
na tela de carregamento. `sotc.ini` e privado e nao entra no git.
Instalacao de PKG: [PKG.md](PKG.md). Pre-cache: [PRECACHE.md](PRECACHE.md).

Para atualizar apenas a visao do upstream, sem sobrescrever mudancas locais:

```bash
git fetch upstream
git log --oneline HEAD..upstream/main
```

A integracao de novos commits deve ser revisada antes de merge.
Ao empacotar no Windows para este fork, use
`SOTC_UPDATE_REPO=CrownParkComputing/ShadowOfTheColossus-PC` para que o pacote
procure releases deste repositorio, conforme o empacotador upstream.
Nenhum binario de release e publicado junto com este check-in.

## Mudancas e validacao

- Build Linux/LP64: includes, caminhos POSIX, tipos inteiros e stubs explicitos
  para integracoes opcionais que dependem do Windows.
- Loader: imagem abaixo de 2 GiB para os ponteiros compactados do jogo;
  recuperacao de leitura especulativa de copias antes de consultar a GPU,
  evitando que os workers esperem pelo mesmo processador que os aguarda.
- Arquivos: lookup sem diferenca de caixa apenas nas montagens do jogo,
  mantendo os saves gravaveis e a protecao contra travessia de diretorios.
- PKG: extracao em blocos, validacao de dados truncados, auxiliar nativo
  AES-XTS e integracao nos scripts de build/empacotamento.
- AppContent Linux: identifica add-ons offline do mesmo titulo e remove
  duplicatas. Reconhecer o direito de acesso nao monta DLC com dados extras.
- Pre-cache Linux: leitura sequencial antes do processo do jogo, com reserva
  de RAM e progresso. O cache do sistema e recuperavel, nao memoria presa.

No ambiente local, o CUSA08034 chegou a selecao de idioma com 30 FPS no limite
padrao e seis direitos de DLC reconhecidos. A leitura antecipada percorreu
13,4 GiB em aproximadamente 42 s. Esses numeros nao sao benchmarks portaveis
nem prova de ausencia de stutter. Shaders ainda desconhecidos precisam ser
compilados na primeira visita.

Os testes focados cobrem extracao sintetica, runner/pre-cache, AppContent,
ponteiros compactados do loader e operacoes de arquivos. A CI testa apenas
ferramentas de fonte e runtime sem GPU; ela nao executa o jogo.
Campanha completa, melhorias de desempenho em gameplay, Windows e AppImage
nao foram validados neste fork. Os relatos de campanha completa nas secoes
historicas do README/CHANGELOG pertencem ao upstream.

Nenhum dump de jogo, DLC, firmware Sony, save, cache, log pessoal ou segredo
de usuario e necessario para clonar ou rodar os testes sinteticos.
