## Athletic Fitness Bulgaria - a HACS integration for Home Assistant

![Downloads](https://img.shields.io/github/downloads/nedevski/hass_athletic_fitness_bulgaria/latest/total?style=flat-square)
![Last release](https://img.shields.io/github/release-date/nedevski/hass_athletic_fitness_bulgaria?style=flat-square)
![Code size](https://img.shields.io/github/languages/code-size/nedevski/hass_athletic_fitness_bulgaria?style=flat-square)
[![Quality Gate](https://img.shields.io/sonar/quality_gate/nedevski_hass_athletic_fitness_bulgaria?server=https%3A%2F%2Fsonarcloud.io&style=flat-square)](https://sonarcloud.io/summary/overall?id=nedevski_hass_athletic_fitness_bulgaria&branch=main)
[![Code coverage](https://img.shields.io/sonar/coverage/nedevski_hass_athletic_fitness_bulgaria?server=https%3A%2F%2Fsonarcloud.io&style=flat-square)](https://sonarcloud.io/component_measures?id=nedevski_hass_athletic_fitness_bulgaria&metric=coverage&view=list)

The Athletic Fitness Bulgaria custom integration allows users to check how many people are currently in Athletic Fitness gyms in Bulgaria.

The integration uses the official Athletic Fitness platform and requires an existing account: [athletic.bg](https://athletic.bg/).

## Installation

Since this is an unofficial integration, you need [HACS (Home Assistant Community Store)](https://hacs.xyz/docs/setup/download).

After installing HACS, open Integrations, search for **Athletic Fitness Bulgaria**, open the integration and click Download.

**You have to restart Home Assistant in order to be able to see the integration!**

After restarting, add the integration as usual:

Settings => Devices and services => Add integration => Athletic Fitness Bulgaria

## How it works

To configure the integration, you need:

- Athletic Fitness account email
- Athletic Fitness account password

During setup, you can choose up to 5 gyms to monitor.

For each selected gym, one sensor entity is created and periodically updated:

- People count ([sensor, int](https://www.home-assistant.io/integrations/sensor/)) - current number of people in that gym

## Notes

- The integration is cloud polling based.
- Data availability depends on Athletic Fitness API availability and your account access rights.

---

If you like my work - consider supporting me.