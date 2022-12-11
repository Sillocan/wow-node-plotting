
# Node Images
{: .no_toc }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Original Images
The original images can be found here [here](https://github.com/Sillocan/wow-node-plotting/tree/main/assets)

---

## The Waking Shores

{% for key in keywords %}
### {{ keyword }}

![]({{ site.baseurl }}/assets/The Waking Shores-{{ include.tag }}-{{ keyword }}.png)
{%- endfor %}

## The Azure Span

{% for key in keywords %}
### {{ keyword }}

![]({{ site.baseurl }}/assets/The Azure Span-{{ include.tag }}-{{ keyword }}.png)
{%- endfor %}

## Ohn'ahran Plains

{% for key in keywords %}
### {{ keyword }}

![]({{ site.baseurl }}/assets/Ohn'ahran Plains-{{ include.tag }}-{{ keyword }}.png)
{%- endfor %}

## Thaldraszus

{% for key in keywords %}
### {{ keyword }}

![]({{ site.baseurl }}/assets/Thaldraszus-{{ include.tag }}-{{ keyword }}.png)
{%- endfor %}

## Stats

```
{% include stats-{{ include.tag }}.txt  %}

```
