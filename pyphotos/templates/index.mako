<%inherit file="base.mako" />

<div class="span4">
<h3>List of albums </h3>
<ul>
%for a in albums:
    <li><a href="/album/${a['title']}/list">${a['title']}</a></li>
%endfor
</ul>

</div>

