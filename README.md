# budget-planner-p3

## Contents

- [Project Aims](#project-aims)
- [User Goals](#user-goals)
- [Site Owner Goals](#site-owner-goals)
- [User Experience](#user-experience-ux)
  - [Target Audience](#target-audience)
  - [User Requirements & Expectations](#user-requirements--expectations)
  - [User Stories](#user-stories)
- [Design](#design)
  - [Wireframes](#wireframes)
- [Features](#features)
  - [App Flow Logic](#app-flow-logic)
  - [Future Ideas / Potential Implementations](#future-ideas--potential-implementations)
- [Technologies Used](#technologies-used)
  - [Languages Used](#languages-used)
  - [Libraries & Programmes Used](#libraries--programmes-used)
- [Testing](#testing)
  - [Automated Testing](#automated-testing)
  - [Manual Testing](#manual-testing)
     - [User Stories](#user-stories)
  - [Bugs](#bugs)
- [Deployment](#deployment)
  - [Heroku Deployment](#heroku-deployment)
  - [How to Fork](#how-to-fork)
  - [How to Clone](#how-to-clone)
- [Credits](#credits)
  - [Content Credits](#content-credits)
  - [Acknowledgements](#acknowledgements)

## Project Aims 
The goal of this project is to create a simple Budget Planner that helps users manage their money by tracking spending and setting monthly goals. The app allows users to sign up, log in, and securely save their data using Google Sheets. Once logged in, users can add transactions, view spending summaries, and set budget goals for different categories.
The budget planner then compares what has been spent against each goal and shows if the user is over or under budget. It runs in on Heroku (an interactive web terminal), so users can access all features easily from a browser without installing anything. The main aim is to make budgeting straigt forward and accessible for everyone.

## User Goals

## Site Owner Goals

## User Experience

## Features
The features section below explains all the features available for the budget planner application. Its important to note that while the "editor" or site owner has all the features available that a regular user does. The editor also has additional functionality that is not available to a regular user and for good reason. 

The budget planner application has been designed to allow for different permissions. This was an important feature as to ensure any "editors" or site owner could make changes on behalf of regular application users if needed. For example a user that was locked out or for whatever reason didnt have access at the time to important information. The editor can act on behalf of the user if requested to maybe add transactions or withdrraw current budget status information. 

Importanlty a regular user does not have any access to other users information and cannot act on their behalf.

### All Users
The features available to all regular users can be seen in the below table. A user firslty signs up or logs in, once succesfully logged in a user can select from any of the below commands. All command options are also listed with descriptions and examples after login.

| Command | What it does | Key options | Example |
|---|---|---|---|
| `signup` | Create an account | — | `bp> signup` |
| `login` | Sign in (sets session) | — | `bp> login` |
| `change-password` | Change your password | `--current`, `--new`, `--confirm` | `bp> change-password` |
| `logout` | Sign out (clears session) | — | `bp> logout` |
| `add-txn` | Add a transaction | `--date YYYY-MM-DD`, `--category`, `--amount`, `--note` | `bp> add-txn` |
| `list-txns` | Show recent transactions | `--date YYYY-MM-DD`, `--limit` | `bp> list-txns --limit 20` |
| `sum-month` | Show monthly total | `--month YYYY-MM` | `bp> sum-month --month 2025-10` |
| `summary` | Totals by category | `--date YYYY-MM-DD` (optional) | `bp> summary` |
| `set-goal` | Set a monthly goal | `--month YYYY-MM`, `--category`, `--amount` | `bp> set-goal --month 2025-10 --category groceries --amount 50` |
| `list-goals` | Show your goals | `--month YYYY-MM` (optional) | `bp> list-goals --month 2025-10` |
| `budget-status` | Compare goals vs spend (diff color-coded) | `--month YYYY-MM` | `bp> budget-status --month 2025-10` |
| `whoami` | Show your account info | — | `bp> whoami` |
| `exit` | exit (ends session) | — | `bp> exit` |
| `menu` | Show menu/instructions | — | `bp> menu` |

#### Login 
Please see the below images relating to login. A user types "login" followed by being asked to enter an email address. Then a password is requested, after this a message is shown to confirm you have logged in successfully or unsuccesfully. Please note password field looks empty due to password hash feature, this is done to protect user entrys. 

| Before entering details | After successful login | Unsuccessful login attempt |
|---|---|---|
| ![Before entering details](assets/images/screenshots/before-login-is-entered.png) | ![After successful login](assets/images/screenshots/after-succesfull-login.png) | ![Unsuccessful login attempt](assets/images/screenshots/unsuccesfull-login-attempt.png) |

#### Signup
Please see the below images relating to signup. A user types "signup" followed by being asked to enter an email address. Then a password is requested to be entered twice to ensure accuracy. After this a message is shown to confirm you have logged in successfully or unsuccesfully. You are then required to login to start using the budget planner.

| Before entering details | After successful singup | Unsuccessful signup attempt |
|---|---|---|
| ![Before entering details](assets/images/screenshots/before-login-is-entered.png) | ![After successful signup](assets/images/screenshots/signup-success.png) | ![Unsuccessful singup attempt](assets/images/screenshots/signup-unsuccessfull.png) |

#### Change Password/logout
In the first image below the change password feature can be seen. This again is hashed as to protect the users new password. A user is required to be firslty logged in before aattempting to change password. The logout feature can be seen in the image on the right, this allows the user to log out form the session after the user has completed any tasks. 

| Change Password | Logout Feature | 
|---|---|
| ![Change Password](assets/images/screenshots/change-password-feature.png) | ![Logout Feature](assets/images/screenshots/logout.png) | 

#### Add transactions/List transactions
A user can add transactions by typing "add-txn" into the terminal. They are then asked to enter the date the transaction took place followed by entering a category. The amount is then entered followed by an optional note entry. A message the appears notifying the user the transaction has been recorded. (Meaning the transaction has succesfully been sent to our transactions google sheet). If a user wishes to see all of their transactions they simply type "list-txns", this provides a list of all their entered transacations (stored on the transactions google sheet) accompanied by dates, categories and notes if entered. (Can be filtered by user for editors)

| Add transactions | List transactions | 
|---|---|
| ![Add transactions](assets/images/screenshots/add-transaction.png) | ![List Transactions](assets/images/screenshots/list-transactions.png) | 

#### Sum Month/Summary
A user can enter "sum-month" to see total spending for a specific month as seen in the first image below. A user can also type "summary" this option provides total spending by category as seen below. 

| Sum Month | Summary | 
|---|---|
| ![Sum Month](assets/images/screenshots/sum-month.png) | ![Summary](assets/images/screenshots/summary.png) | 

#### Set Goal/List Goal
Users can set goals by typing "set-goal". This feature allows users to esentially set their budget allowance per month and category, then selecting the amount they do not wish to exceed. "list-goals" then allows for all goals to be viewed as per the below image.

| Set Goal | List Goal | 
|---|---|
| ![Set Goal](assets/images/screenshots/set-goal.png) | ![List Goal](assets/images/screenshots/list-goals.png) | 

#### Budget Status
This feature is a continuation from the set/list goals feature. This shows each category of budget with the goal and actual spend. As well as the difference to show if the user is acheving the set goal or falling short. Postive numbers are green and negative numbers appear in red to highlight this.

| Budget Status | 
|---|
| ![Budget Status](assets/images/screenshots/budget-status.png) |

#### Whoami/Exit/Menu
The whoami feature allows users to double check what account they are logged into. Shows email user ID and the date the account was created.
The exit feature allows users to exit the terminal (Without a log back in option). The menu feature allows for users to type "menu" if they are confused about any of the features and how to run them. 

| whoami feature | exit feature | menu feature |
|---|---|---|
| ![whoami](assets/images/screenshots/whoami.png) | ![exit](assets/images/screenshots/exit.png) | ![menu](assets/images/screenshots/menu-normal.png) |

### Editor Only
An editor has all the regular features at their disposal for personal details if they so wish. However, there are some additional capabilites/features for editors as seen in the below table. Editors can carry out tasks and retract information on the behalf of regular users if needed. Editors can also select roles (this is not optional for regular users). Once signed in the "user" or "editor" role is assigned to ensure what can and cannot be accessed. 

| Capability | Command/How | Example |
|---|---|---|
| Act on another user’s data | Pass `--email` to self-scoped commands | `list-txns --email user@example.com`; `list-goals --email user@example.com --month 2025-10`; `sum-month --email user@example.com --month 2025-10`; `summary --email user@example.com`; `budget-status --email user@example.com --month 2025-10`; `whoami --email user@example.com` |
| Manage roles | `set-role --email <user> --role editor\|user` | `set-role --email user@example.com --role editor` |
| List users | `list-users [--limit N]` | `list-users --limit 10` |

#### Manage Roles/List Users (Editor only)
An editor can change the permisions on any user from "user" to "editor" if they wish. All users are regular "users" by default. As seen in the image below the editor simply types  "set-role" for the option to change a users role to appear. the list users function can be seen in the other image below. This function again is strictly only for editors. Regular users do not have permisions to view this information. 

#### Act on another users data (Editors only - example)
As seen in the image below and editor can access other users data or add a transaction if needed. This is a feature that was added in the case of emergency for any user that they could reach out to an editor for important information. The below example shows how an editor would view another users transaction.


| Manage Roles | List Users | List users transactions |
|---|---|---|
| ![Manage Roles](assets/images/screenshots/set-role-editor.png) | ![List Users](assets/images/screenshots/list-users-editor.png) | ![list transactions editor](assets/images/screenshots/list-txns-email-editor.png) |

#### Different menu view (editiors vs user)
Another imporant feature is the different menus available depending on whos logged in. AN editor has more functionality then a standard user and so the menu is more descriptive with more options. Its also important that any commands specific to an editor are not listed for users to see, as to avoid confusion.

| Editor menu | User Menu | 
|---|---|
| ![Editor Menu](assets/images/screenshots/instructions-editor.png) | ![User Menu](assets/images/screenshots/instructions-user.png) |

### Additional Features
Some additional features of how the budget planner application behaves behind the scenes can be seen below.

- Roles are in the `Role` sheet (`email`, `role`). Missing entries default to `user`. This is an important feature as to differentiate between permissions.
- Session variables (web terminal): `BP_EMAIL` (logged-in user), `BP_ROLE` (editor/user).
- Headings and separators are styled for readability. Key figures/information are also highlighted for the same reason.
- Added Terminal features for UX: `help` and `help <command>`, typos suggest “Did you mean …”, `Ctrl+C` cancels prompts; after login.
- Commands use the session email by default as this is better practice then a user having to constantly confirm who they are.

### App flow logic 
The below diagram shows how the app works from start to finish. You open the budget planner and either sign up or log in. After a successful login, the app retains the user information so you don’t need to enter your email again. From there you can choose commands like adding a transaction, listing transactions, setting or listing goals, checking budget status (with psotive/negative differences), viewing a summary, or changing your password. 
You can also show the menu, log out to end your session, or exit to close the terminal. If you are an editor, you also get extra options like listing users and setting roles, and you can act on another user’s data when needed.

![App Flow Logic](assets/images/design/app-flow-logic.png)


### Future Ideas / Potential Implementations
There are many growth possibilites for the budget planner in the future. Below I have listed some of the main ideas that could be implemented going forward to really take it up a level and improve the overall offering to the users. 

| Future idea | Comments |
|---|---|
| Password reset with email confirmation | Let users request a reset, send a code or link to their email, verify it, then allow a new password. |
| CSV downloads | Let users download transactions, goals and summaries as CSV (for a month or all time). Good for backups or sharing. |
| Charts and trends | Show simple graphs of spend versus goals by month so progress is easy to see. |
| Recurring transactions | Let users mark bills or subscriptions as recurring so they auto‑add each month. |
| Alerts/notifications | Optional alerts when a category is close to or over its goal, or when a large transaction is added. |
| Two-factor login  | Add an extra step during login (code from email/app) for more security. |

## Testing

### Code Validation
All Python files in this project were tested regularly throughout development. Each time a new feature or update was added, the code was checked using the terminal to make sure all commands worked correctly and no errors appeared. The files were also reviewed using PEP8 standards to make sure they followed formatting rules, such as correct indentation and line length.

All Python files were also tested using the Code Institute Python Linter, which checks that the code meets PEP8 requirements. No major errors were found, and any small warnings were fixed to ensure the project followed professional standards, as seen below.

#### auth.py
Please see the CI Python Linter test passed for auth.py below with no errors found.
![auth.py CI pass](assets/images/testing/auth.py-clear.png)

#### budgets.py
Please see the CI Python Linter test passed for budgets.py below with no errors found.
![budgets.py CI pass](assets/images/testing/budget.py-clear.png)

#### constants.py
Please see the CI Python Linter test passed for constants.py below with no errors found.
![constants.py CI pass](assets/images/testing/constants.py-clear.png)

#### index.py
Please see the CI Python Linter test passed for index.py below with no errors found.
![index.py CI pass](assets/images/testing/index.py-clear.png)

#### __main__.py
Please see the CI Python Linter test passed for __main__.py below with no errors found.
![__main__.py CI pass](assets/images/testing/main.py-clear.png)

#### models.py
Please see the CI Python Linter test passed for models.py below with no errors found.
![models.py CI pass](assets/images/testing/models.py-clear.png)

#### reports.py
Please see the CI Python Linter test passed for reports.py below with no errors found.
![reports.py CI pass](assets/images/testing/reports.py-clear.png)

#### run.py
Please see the CI Python Linter test passed for run.py below with no errors found.
![run.py CI pass](assets/images/testing/run.py-clear.png)

#### run_interactive.py
Please see the CI Python Linter test passed for run_interactive.py below with no errors found.
![run_interactive.py CI pass](assets/images/testing/run_interactive.py-clear.png)

#### sheets_gateway.py
Please see the CI Python Linter test passed for sheets_gateway.py below with no errors found.
![sheets_gateway.py CI pass](assets/images/testing/sheets.gateway.py-clear.png)

#### transactions.py
Please see the CI Python Linter test passed for transactions.py below with no errors found.
![transactions.py CI pass](assets/images/testing/transactions.py-clear.png)

#### validation.py
Please see the CI Python Linter test passed for validation.py below with no errors found.
![validation.py CI pass](assets/images/testing/validation.py-clear.png)

### Manual Testing

#### Features 

| Feature | Expected outcome | Results |
|---|---|---|
| Signup | Creates a new user and shows a success message. | works as should |
| Login | Accepts correct email/password and logs the user in. | works as should |
| Change password | Asks for current password, updates to a new one if correct. | works as should |
| Logout | Clears the saved session so commands require login again. | works as should |
| Add transaction | Saves a row with date, category, amount and note. | works as should |
| List transactions | Shows recent transactions for the logged‑in user. | works as should |
| Sum month | Shows the total spend for a given month. | works as should |
| Summary | Shows totals by category (for a date if given). | works as should |
| Set goal | Stores a monthly goal for a category and month. | works as should |
| List goals | Lists saved goals (optionally filter by month). | works as should |
| Budget status | Compares goals vs spend and colors the difference. | works as should |
| Whoami | Shows the current user’s id, email and created date. | works as should |
| Menu/Help | Prints the guide with commands and examples. | works as should |
| Exit | Leaves the terminal session cleanly. | works as should |
| Editor: list-users | Shows user list (editor only). | works as should |
| Editor: set-role | Changes a user’s role to user/editor (editor only). | works as should |
| Editor: per‑user filters | Editor can use --email to act on another user when allowed. | works as should |


#### User Stories 