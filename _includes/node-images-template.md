{% assign zones = "Isle of Dorn, The Ringing Deeps, Hallowfall, Azj-Kahet" | split: ", " %}
{% assign prefixes = include.prefixes | split: " " | sort_natural %}

# {{ include.tag }}
{: .no_toc }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Original Images
The original images can be found here [here](https://github.com/Sillocan/wow-node-plotting/tree/main/assets)

---

## By Zone
{% for zone in zones %}

### {{ zone }}

[![{{ zone }} - {{include.tag}} - all]({{ site.baseurl }}/assets/{{ zone }}-{{ include.tag }}-all.png)]({{ site.baseurl }}/assets/{{ zone }}-{{ include.tag }}-all.png)
{% endfor %}

---

## By Prefix

Where `None` means there is no prefix -- just a basic node.
{% for key in prefixes %}

### {{ key }}

{% for zone in zones %}
[![{{ zone }} - {{ include.tag }} - {{ key }}]({{ site.baseurl }}/assets/{{ zone }}-{{ include.tag }}-{{ key }}.png)]({{ site.baseurl }}/assets/{{ zone }}-{{ include.tag }}-{{ key }}.png)
{% endfor %}
---
{% endfor %}

## Stats

```
{% include stats-{{ include.tag }}.txt  %}

```
