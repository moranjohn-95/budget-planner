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
This feature is a continuation from the set/list goals feature. This shows each category of budget with the goal and actual spend. As well the difference to show if the user is acheving the set goal or falling short. 

| Budget Status | 
|---|
| ![Budget Status](assets/images/screenshots/budget-status.png) |


### Editor Only

There are some additional capabilites/features for editors as seen in the below table. Editors can carry out tasks and retract information on the behalf of regular users if needed. Editors can also select roles (this is not optional for regular users). Once signed in the "user" or "editor" role is assigned to ensure what can and cannot be accessed. 

| Capability | Command/How | Example |
|---|---|---|
| Act on another user’s data | Pass `--email` to self-scoped commands | `list-txns --email user@example.com`; `list-goals --email user@example.com --month 2025-10`; `sum-month --email user@example.com --month 2025-10`; `summary --email user@example.com`; `budget-status --email user@example.com --month 2025-10`; `whoami --email user@example.com` |
| Manage roles | `set-role --email <user> --role editor\|user` | `set-role --email user@example.com --role editor` |
| List users | `list-users [--limit N]` | `list-users --limit 10` |

### Additional Features
Some additional features of how the budget planner application behaves behind the scenes can be seen below.

- Roles are in the `Role` sheet (`email`, `role`). Missing entries default to `user`. This is an important feature as to differentiate between permissions.
- Session variables (web terminal): `BP_EMAIL` (logged-in user), `BP_ROLE` (editor/user).
- Headings and separators are styled for readability. Key figures/information are also highlighted for the same reason.
- Added Terminal features for UX: `help` and `help <command>`, typos suggest “Did you mean …”, `Ctrl+C` cancels prompts; after login.
- Commands use the session email by default as this is better practice then a user having to constantly confirm who they are.


