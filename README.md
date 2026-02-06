# ManutFlow - Sistema de Gerenciamento de Manutenções

**Versões:** [Português](#) | [English](#)

---

## ManutFlow (Português)

###  Descrição

Este é o **ManutFlow**, um sistema completo e inteligente para o gerenciamento de equipamentos e manutenções, desenvolvido para otimizar a gestão do parque de máquinas em empresas e indústrias. A principal inovação desta solução é a integração com a **API do Groq**, que permite análises preditivas e insights valiosos sobre a saúde dos equipamentos, priorização de intervenções e otimização de custos. O sistema foi projetado para ser eficiente, de baixo custo operacional e fácil de usar, seguindo o padrão arquitetural MVC para garantir organização e manutenibilidade.

###  Funcionalidades Principais

O ManutFlow oferece um conjunto robusto de funcionalidades para uma gestão de manutenção eficaz:

*   **Gerenciamento de Equipamentos:**
    *   Cadastro detalhado e controle de status (Ativo, Em Manutenção, Sucateado).
    *   Visualização rápida do estado dos equipamentos através de indicadores visuais.

*   **Registro e Histórico de Manutenções:**
    *   Registro completo de manutenções preventivas e corretivas.
    *   Controle de custos associados a cada manutenção.
    *   Descrições técnicas detalhadas para cada intervenção.

*   **Módulo de Inteligência Artificial (Groq Cloud):**
    *   **Resumo de Saúde:** Análise qualitativa do estado geral do parque de máquinas.
    *   **Priorização Inteligente:** Sugestão de equipamentos que necessitam de atenção imediata com base em dados preditivos.
    *   **Insights de Custo:** Identificação de setores e equipamentos com maiores gastos de manutenção.
    *   **Recomendações Estratégicas:** Sugestões para otimização de processos e redução de falhas.
    *   **Análise Preditiva:** Cálculo do MTBF (Tempo Médio Entre Falhas) e estimativa da próxima falha para equipamentos com histórico de manutenções corretivas.

*   **Autenticação e Autorização:**
    *   Sistema de Login e Cadastro de usuários.
    *   Funcionalidade de Recuperação de Senha.
    *   Perfis de usuário com informações personalizadas e histórico de atividades.
    *   Controle de acesso baseado em perfis (Administrador e Funcionário).

*   **Notificações e Agendamentos:**
    *   Mecanismo de notificações para alertar sobre manutenções preventivas próximas.
    *   Agendamento de manutenções preventivas, com notificação para o responsável pelo equipamento e administradores.

*   **Exportação de Dados:**
    *   Funcionalidade para exportar relatórios de manutenções para o formato CSV (compatível com Excel), facilitando a análise externa.

*   **Estrutura MVC:**
    *   Organização do código seguindo o padrão Model-View-Controller para facilitar a manutenção e escalabilidade.

###  Tecnologias Utilizadas

O ManutFlow foi construído utilizando as seguintes tecnologias:

*   **Backend:** Python 3.11, Flask, Flask-SQLAlchemy, python-dotenv, Flask-Login.
*   **Banco de Dados:** SQLite (com SQLAlchemy para ORM).
*   **Inteligência Artificial:** Groq Cloud API (utilizando modelos como Llama 3.3 70B para análise preditiva).
*   **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js.

###  Como Utilizar

Para colocar o ManutFlow em funcionamento, siga os passos abaixo:

#### 1. Obter Chave API do Groq

1.  Acesse o [Groq Cloud Console](https://console.groq.com/).
2.  Crie uma conta gratuita.
3.  Navegue até a seção "API Keys" e gere uma nova chave.

#### 2. Configurar o Ambiente

Após extrair o projeto, navegue até a pasta raiz do projeto e instale as dependências listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### 3. Definir a Chave API

Defina sua chave API do Groq como uma variável de ambiente chamada `GROQ_API_KEY`. Substitua `sua_chave_aqui` pela chave que você gerou.

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

#### 4. Executar o Sistema

Com as dependências instaladas e a chave API configurada, execute o aplicativo:

```bash
python app.py
```

O sistema estará acessível em `http://localhost:5000`.

###  Contribuições

As seguintes pessoas contribuíram para o desenvolvimento do ManutFlow:

*   **amand4morais:**
    *   Implementação de temas claro e escuro.
    *   Adição de funcionalidades de IA preditiva.
    *   Exportação de tabelas para Excel.
    *   Correções na barra de navegação e filtros.
    *   Adição de página de destino (landing page).
    *   Implementação da funcionalidade de recuperação de senha.
    *   Desenvolvimento de filtros de IA.
    *   Ajustes automáticos de ano.
    *   Criação do protótipo inicial do projeto.
    *   Diversas pequenas alterações e correções de interface.

*   **JoseMarra2006:**
    *   Adição da data de membro.
    *   Tratamento de erros de login.
    *   Implementação da funcionalidade de linha do tempo.
    *   Desenvolvimento do mecanismo de notificações.
    *   Correções de erros gerais.
    *   Implementação de restrição de acesso para funcionários ocultos.
    *   Adição do logo da águia.
    *   Funcionalidade de visualização de perfil por administrador.
    *   Criação do perfil de usuário.
    *   Restrição de usuário.
    *   Restrição de administrador.
    *   Adição de tabelas de funcionários e setores.
    *   Limpeza do banco de dados.
    *   Tratamento de exceções.

---

## ManutFlow (English)

###  Description

This is **ManutFlow**, a complete and intelligent system for equipment and maintenance management, developed to optimize the machine park management in companies and industries. The main innovation of this solution is the integration with the **Groq API**, which allows predictive analysis and valuable insights into equipment health, intervention prioritization, and cost optimization. The system is designed to be efficient, with low operational cost, and easy to use, following the MVC architectural pattern to ensure organization and maintainability.

###  Key Features

ManutFlow offers a robust set of functionalities for effective maintenance management:

*   **Equipment Management:**
    *   Detailed registration and status control (Active, Under Maintenance, Scrapped).
    *   Quick visualization of equipment status through visual indicators.

*   **Maintenance Registration and History:**
    *   Complete registration of preventive and corrective maintenance.
    *   Cost control associated with each maintenance.
    *   Detailed technical descriptions for each intervention.

*   **Artificial Intelligence Module (Groq Cloud):**
    *   **Health Summary:** Qualitative analysis of the overall machine park status.
    *   **Intelligent Prioritization:** Suggestion of equipment that needs immediate attention based on predictive data.
    *   **Cost Insights:** Identification of sectors and equipment with higher maintenance costs.
    *   **Strategic Recommendations:** Suggestions for process optimization and failure reduction.
    *   **Predictive Analysis:** Calculation of MTBF (Mean Time Between Failures) and estimation of the next failure for equipment with a history of corrective maintenance.

*   **Authentication and Authorization:**
    *   User Login and Registration system.
    *   Password Recovery functionality.
    *   User profiles with personalized information and activity history.
    *   Access control based on profiles (Administrator and Employee).

*   **Notifications and Scheduling:**
    *   Notification mechanism to alert about upcoming preventive maintenance.
    *   Scheduling of preventive maintenance, with notification to the equipment responsible and administrators.

*   **Data Export:**
    *   Functionality to export maintenance reports to CSV format (Excel compatible), facilitating external analysis.

*   **MVC Structure:**
    *   Code organization following the Model-View-Controller pattern to facilitate maintenance and scalability.

###  Technologies Used

ManutFlow was built using the following technologies:

*   **Backend:** Python 3.11, Flask, Flask-SQLAlchemy, python-dotenv, Flask-Login.
*   **Database:** SQLite (with SQLAlchemy for ORM).
*   **Artificial Intelligence:** Groq Cloud API (using models like Llama 3.3 70B for predictive analysis).
*   **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js.

###  How to Use

To get ManutFlow up and running, follow the steps below:

#### 1. Obtain Groq API Key

1.  Access the [Groq Cloud Console](https://console.groq.com/).
2.  Create a free account.
3.  Navigate to the "API Keys" section and generate a new key.

#### 2. Configure the Environment

After extracting the project, navigate to the project's root folder and install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### 3. Set the API Key

Set your Groq API key as an environment variable named `GROQ_API_KEY`. Replace `your_key_here` with the key you generated.

**On Windows (Command Prompt):**

```cmd
set GROQ_API_KEY=your_key_here
```

**On Windows (PowerShell):**

```powershell
$env:GROQ_API_KEY="your_key_here"
```

**On Linux/Mac:**

```bash
export GROQ_API_KEY="your_key_here"
```

#### 4. Run the System

With the dependencies installed and the API key configured, run the application:

```bash
python app.py
```

The system will be accessible at `http://localhost:5000`.

### 👥 Contributions

The following individuals contributed to the development of ManutFlow:

*   **amand4morais:**
    *   Implementation of light and dark themes.
    *   Addition of predictive AI functionalities.
    *   Export of tables to Excel.
    *   Fixes in the navigation bar and filters.
    *   Addition of a landing page.
    *   Implementation of the password recovery feature.
    *   Development of AI filters.
    *   Automatic year adjustments.
    *   Creation of the initial project prototype.
    *   Various minor changes and interface corrections.

*   **JoseMarra2006:**
    *   Addition of member date.
    *   Login error handling.
    *   Implementation of the timeline functionality.
    *   Development of the notification mechanism.
    *   General error fixes.
    *   Implementation of access restriction for hidden employees.
    *   Addition of the eagle logo.
    *   Profile viewing functionality by administrator.
    *   User profile creation.
    *   User restriction.
    *   Administrator restriction.
    *   Addition of employee and sector tables.
    *   Database cleanup.
    *   Exception handling.
