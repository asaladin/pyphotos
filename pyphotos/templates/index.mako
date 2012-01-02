<%inherit file="base.mako" />

List of albums:
%for a in albums:
    ${a['title']} <br />    
%endfor