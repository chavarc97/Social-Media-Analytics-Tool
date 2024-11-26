from Dgrah.client import main as clientMain


def main():
    try:

        clientMain()
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    main()