# **🤙 LIBRASCONTROLLER**

Um software que reconhece gestos de Libras e gestos customizados e os transforma em input de teclado ou mouse.

_🚧 PROJETO EM DESENVOLVIMENTO 🚧_

---

## **📖 SOBRE O PROJETO**

O **LibrasController** utiliza comunicação via WebSocket entre o backend (Python) e o frontend (JavaScript/TypeScript) para:

- Capturar frames da câmera selecionada pelo usuário usando **OpenCV**.
- Processar a posição da mão com **MediaPipe**.
- Reconhecer gestos por meio de um algoritmo próprio.
- Enviar comandos de teclado e mouse em nível baixo (low-level) usando **C**.

---

## **🛠️ COMO INSTALAR**

### 1️⃣ **Pré-requisitos**
Certifique-se de que você possui:
- Python (>=3.8)
- Node.js (>=16.0)
- Gerenciador de pacotes `pip` e `npm`.

### 2️⃣ **Instalação**
Clone o repositório (ou faça o download manualmente do repositório):
```bash
git clone https://github.com/ofelipelucca/librascontroller.git

cd librascontroller
```

Instale as dependências do backend (Python):
```bash
pip install -r requirements.txt
```

Instale as dependências do frontend (JavaScript/TypeScript):
```bash
npm install
```

### 3️⃣ **Build**
Para construir o projeto:
```bash
npm run build
```

### 4️⃣ **Execução**
Inicie o software:
```bash
npm run start
```

---

## **👨‍💻 TECNOLOGIAS UTILIZADAS**

- **Python**: Backend e reconhecimento de gestos.
- **TypeScript/JavaScript**: Frontend.
- **Node.js**: Comunicação e integração.
- **Electron**: Interface desktop.
- **React**: Construção da interface gráfica.
- **OpenCV**: Processamento de imagens.
- **MediaPipe**: Estimativa da posição da mão.

---

![GitHub Repo stars](https://img.shields.io/github/stars/ofelipelucca/librascontroller?style=social)
![GitHub forks](https://img.shields.io/github/forks/ofelipelucca/librascontroller?style=social)
![GitHub issues](https://img.shields.io/github/issues/ofelipelucca/librascontroller)
![GitHub last commit](https://img.shields.io/github/last-commit/ofelipelucca/librascontroller)
![Repo size](https://img.shields.io/github/repo-size/ofelipelucca/librascontroller)
![GitHub](https://img.shields.io/github/license/ofelipelucca/librascontroller)
___

**Envie um pull request :)**

[![](https://contrib.rocks/image?repo=ofelipelucca/librascontroller)](https://github.com/ofelipelucca/librascontroller/graphs/contributors)
