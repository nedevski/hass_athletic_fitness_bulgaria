# Athletic Fitness Bulgaria - **неофициална** интеграция за Home Assistant


![Downloads](https://img.shields.io/github/downloads/nedevski/hass_athletic_fitness_bulgaria/latest/total?style=flat-square)
![Last release](https://img.shields.io/github/release-date/nedevski/hass_athletic_fitness_bulgaria?style=flat-square)
![Code size](https://img.shields.io/github/languages/code-size/nedevski/hass_athletic_fitness_bulgaria?style=flat-square)
[![Quality Gate](https://img.shields.io/sonar/quality_gate/nedevski_hass_athletic_fitness_bulgaria?server=https%3A%2F%2Fsonarcloud.io&style=flat-square)](https://sonarcloud.io/summary/overall?id=nedevski_hass_athletic_fitness_bulgaria&branch=main)
[![Code coverage](https://img.shields.io/sonar/coverage/nedevski_hass_athletic_fitness_bulgaria?server=https%3A%2F%2Fsonarcloud.io&style=flat-square)](https://sonarcloud.io/component_measures?id=nedevski_hass_athletic_fitness_bulgaria&metric=coverage&view=list)
![Athletic logo](/images/banner.png)

Интеграцията с **Athletic Fitness** позволява да се проверява колко хора се намират в момента в залите на Athletic Fitness. Това е независим проект, който **не е** свързан по никакъв начин с официалния екип на Атлетик Фитнес.


Данните се извличат от официалната платформа на Athletic Fitness, което изисква да имате регистрация на [athletic.bg](https://athletic.bg/).

## Инсталиране

Тъй като това е неофициална интеграция, е необходимо да имате инсталиран [HACS (Home Assistant Community Store)](https://hacs.xyz/docs/setup/download).

Най-лесния начин за инсталация е с бутона долу:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Nedevski&repository=hass_athletic_fitness_bulgaria&category=integration)

Алтернативно, можете да я инсталирате ръчно:

Тъй като интеграцията все още не е добавена в HACS. Заради това трябва от HACS страницата в Home Assistant да се изберат трите точки горе вдясно и да се избере "Custom repository" и се добавя `https://github.com/nedevski/hass_athletic_fitness_bulgaria`.
Това ще добави репото в регистъра на вашия HACS и интеграцията ще може да бъде намерена с търсачката.

**Трябва да рестартирате Home Assistant, за да може интеграцията да се появи на страницата с интеграции!**

След рестартиране добавете интеграцията по стандартния начин:

Settings => Devices and services => Add integration => Athletic Fitness Bulgaria

## Как работи

За да конфигурирате интеграцията, са необходими вашите данни за вход в Athletic Fitness – имейл и парола.

По време на настройката можете да изберете до 5 зали, които да наблюдавате.

За всяка избрана зала се създава отделен сензор, който се обновява на всеки 5 минути:

- Брой хора (sensor, int) – текущият брой хора в съответната зала

![Screenshot](/images/screenshot-en.png)

## Бележки

- Интеграцията използва cloud polling.
- Точността на данните зависи от официалното приложение на Athletic Fitness.

---

Ако харесвате работата ми, почерпете ме с 1 бира в Ko-Fi:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/nedevski/tip)

---

# Athletic Fitness Bulgaria - a HACS integration for Home Assistant

The Athletic Fitness Bulgaria custom integration allows users to check how many people are currently in Athletic Fitness gyms in Bulgaria. This is an independent project that is **not affiliated** in any way with the official Athletic Fitness team.

The integration uses the official Athletic Fitness platform and requires an existing account: [athletic.bg](https://athletic.bg/).

## Installation

Since this is an unofficial integration, you need to have [HACS (Home Assistant Community Store)](https://hacs.xyz/docs/setup/download) installed.

The easiest way to install it is using the button below:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Nedevski&repository=hass_athletic_fitness_bulgaria&category=integration)

Alternatively, you can install it manually:

Since the integration is not yet added to HACS, you need to go to the HACS page in Home Assistant, click the three dots in the top right corner, select "Custom repository", and add `https://github.com/nedevski/hass_athletic_fitness_bulgaria`.

This will add the repository to your registry, and the integration will become searchable in HACS.

**You need to restart Home Assistant for the integration to appear on the integrations page!**

After restarting, add the integration as usual:

Settings => Devices and services => Add integration => Athletic Fitness Bulgaria

## How it works

To configure the integration, you need your Athletic Fitness account - email and password

During setup, you can choose up to 5 gyms to monitor.

For each selected gym, one sensor entity is created and updated every 5 minutes:

- People count ([sensor, int](https://www.home-assistant.io/integrations/sensor/)) - current number of people in that gym

![Screenshot](/images/screenshot-en.png)

## Notes

- The integration is cloud polling based.
- Data availability depends on Athletic Fitness API availability.

---

If you like my work - consider supporting me:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/nedevski/tip)
