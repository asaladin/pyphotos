<%inherit file="base.mako" />

List of albums:
%for a in albums:
    <a href="/album/${a['title']}"> ${a['title']} </a> <br />    
%endfor