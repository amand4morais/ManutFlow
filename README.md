# Sistema de Controle de Manutenção de Equipamentos (Versão Groq)

Sistema completo para gerenciamento de equipamentos e manutenções com análise inteligente utilizando a API do Groq.

## 📋 Descrição

Este sistema foi desenvolvido para empresas e indústrias que necessitam de um controle rigoroso de seu parque de máquinas. A grande vantagem desta versão é a integração com o **Groq**, que oferece modelos de IA extremamente rápidos (como o Llama 3) e um nível gratuito generoso.

## ✨ Funcionalidades

### 1. Gerenciamento de Equipamentos
- Cadastro completo e controle de status (Ativo, Manutenção, Sucateado).
- Cores indicativas para visualização rápida do estado do parque.

### 2. Registro de Manutenções
- Histórico de manutenções preventivas e corretivas.
- Controle de custos e descrições técnicas.

### 3. Módulo de IA (Groq Cloud)
- **Resumo de Saúde**: Análise qualitativa do estado geral.
- **Priorização**: Sugestão de quais máquinas precisam de atenção imediata.
- **Insights de Custo**: Identificação de setores com maiores gastos.
- **Recomendações**: Sugestões estratégicas para otimização da manutenção.

## 🛠️ Tecnologias

- **Backend**: Python 3.11 + Flask
- **Banco de Dados**: SQLite (SQLAlchemy)
- **IA**: Groq Cloud API (Llama 3.3 70B)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js

## 📦 Instalação e Configuração

### 1. Obter Chave API do Groq
1. Acesse [Groq Cloud Console](https://console.groq.com/)
2. Crie uma conta gratuita.
3. Vá em "API Keys" e gere uma nova chave.

### 2. Configurar o Ambiente
Extraia o projeto e, na pasta raiz, instale as dependências:
```bash
pip install -r requirements.txt
```

### 3. Definir a Chave API
Você deve colocar sua chave em uma variável de ambiente chamada `GROQ_API_KEY`.

**No Windows (Prompt de Comando):**
```cmd
set GROQ_API_KEY=sua_chave_aqui
```

**No Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="sua_chave_aqui"
```

**No Linux/Mac:**
```bash
export GROQ_API_KEY="sua_chave_aqui"
```

### 4. Executar o Sistema
```bash
python app.py
```
Acesse: `http://localhost:5000`

## 📊 Estrutura MVC
O projeto segue o padrão Model-View-Controller para garantir organização e facilidade de manutenção, separando a lógica de banco de dados, a interface do usuário e as regras de negócio.

---
**Desenvolvido com foco em eficiência e baixo custo operacional.**
