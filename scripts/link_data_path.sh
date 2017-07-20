
# if [ "$(uname)" == "Darwin" ]; then

case "$(uname -s)" in
  Darwin)
    echo 'Link data path for Mac OS'
    ln -s ~/data/projects/local-embedding ../data
    ;;
  Linux)
    echo 'Link data path for Linux'
    ln -s /shared/data/czhang82/projects/local-embedding ../data
    ;;
esac

