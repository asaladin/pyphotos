<%inherit file="base.mako" />

<a href="/login"> login </a>  <br />
List of albums:
%for a in albums:
    <a href="/album/${a['title']}/list"> ${a['title']} </a> <br />    
%endfor