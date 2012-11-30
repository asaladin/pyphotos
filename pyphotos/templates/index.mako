<%inherit file="base.mako" />


<h3>List of albums </h3>
<ul>
%for a in albums:
    <li><a href="/album/${a['title']}/list">${a.owner}/${a['title']}</a></li>
%endfor
</ul>



