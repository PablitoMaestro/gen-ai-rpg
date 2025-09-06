I would like to use the following setup of my repo:
- One folder with nano-banana-hackathon-kit (it's already there)
- One folder called frontend
- One folder called backend
- One folder called supabase

We will be using Claude Code CLI for development, We will also use ref MCP to check for external documentation whenever it's needed. Also, for nano banana examples, we can check inside the root folder of nano banana. 

For the backend, we will be using FastAPI and Pydantic. We must write with an async support. We should have the following folders:
- services
- scripts  Also, the other folders as per recommended best practices.

Frontend should be running on TypeScript with React and Next.js. We will deploy it on Vercel. We should start from running the official starter template of Next.js inside the frontend folder. Also, we should use Zod for validation and Zustand for client state management. We should have strict typecheck and lint rules. We should follow best practices and simplistic architecture. We should call backend whenever actions involving external APIs are needed. We should use Tailwind CSS, by the way.

In the supabase folder, we should handle the seed, we should handle migrations and so on. We should simply start the new project init supabase following their official CLI documentation within the supabase folder. 

Back-end will be deployed on Scaleway container, front-end will be deployed on Vercel. Supabase will have one db that is local and this local db should be only edited via migrations. We should use Supabase's official CLI and commands to manage it, and for the online Supabase, we should have for now one main production database which should be managed via MCP or CLI. However, we should Always use official CLI commands for pushing from local to the online project. 

We should have one main branch in GitHub and one dev branch. We should be only merging from dev into main, only if there are no TypeCheck and Lint errors, and if everything is ok. But for now, let's keep things simple anyway.

We need to set up the structure of the project. Let's start with the official Next.js template.

And for the frontend, we should First focus on creating the main game view where we start by creating a character. To create the character, we should be able to choose from:
1. Gender (male or female)
2. If it's male, then we should be able to choose from 4 male portraits
3. If it's female, then we should also be able to choose from 4 female portraits
4. As an alternative, we can upload our own profile picture

We should have those male and female portraits, I think, uploaded to Supabase to store them so that we are able to choose from them. Once we need those portraits, just prompt me, and I will upload the files for you. And then we should be also able to create the image of our character, a full-body image using Nano Banana API. Overall, this whole interface of our game should be full-screen and be very modern and animating, following best practices, minimalistic, classic dark fantasy RPG style yet beautiful. The user should be able to have 4 portraits or full-body builds generated for him, and in parallel, we must make sure to call the Nano Banana API asynchronously in parallel so that all 4 builds are ready for the user to choose from. Once the build is chosen and the game starts, we should save that build for the user, and that build will be later used in generating other images of the story. Let's focus on that stage 1: Setting up the project and setting up the first character development view. Later, we will together figure out how to construct this game further which is a text-based RPG game with custom AI-generated images of the character that is put into different scenes. Once we are done with that, we will start thinking of Eleven Labs implementation also, but for now, let's focus on first steps only. Whenever we have a big thing to do, we should save it into a plan.md file. And we should consecutively check the checkpoints. 

Overall, it is important that we follow a dry methodology. So don't repeat yourself. We should keep our code clean, modular, based on the services. The code that is easily scalable. And yet we should aim for maximum simplicity. This is a prototype or an MVP for a hackathon that later might be changed into a production-ready code. But for now we should focus on maximum simplicity, no overcomplications, and whenever you plan something double-check if you can achieve the same goal with more minimal code changes and overall simpler and more efficient code.