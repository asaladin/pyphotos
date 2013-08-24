<%inherit file="base.mako" />


<h3>List of albums </h3>
<ul>
%for a in albums:
    <li><a href="/album/${a.name}/list">${a.name}</a></li>
%endfor
</ul>


