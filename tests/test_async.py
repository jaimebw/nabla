import asyncio

async def execute_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    output, outerror = await process.communicate()
    return output, outerror

async def main():
    commands = [
        "ls",
        "cd 1",
        "ls"
        # Add more commands here
    ]
    commands = " && ".join(commands)
    output, outerror = await execute_command(commands)
    print(f"Output: {output}")
    print(f"Error: {outerror}")

if __name__ == "__main__":
    asyncio.run(main())

