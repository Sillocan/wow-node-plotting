{% assign zones = "The Waking Shores, The Azure Span, Ohn'ahran Plains, Thaldraszus, Valdrakken" | split: ", " %}
{% assign keywords = include.keywords | split: " " %}

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

![]({{ site.baseurl }}/assets/{{ zone }}-{{ include.tag }}-all.png)
{% endfor %}

---

## By Keyword

Where `None` means there is no keyword -- just a basic node.
{% for key in keywords %}

### {{ key }}

{% for zone in zones %}
![]({{ site.baseurl }}/assets/{{ zone }}-{{ include.tag }}-{{ key }}.png)
{% endfor %}
---
{% endfor %}

## Stats

```
{% include stats-{{ include.tag }}.txt  %}

```
