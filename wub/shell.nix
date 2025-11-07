with import <nixpkgs> {};
  ruby.withPackages (
    ps:
      with ps; [
        nokogiri
        pry
      ]
  )
