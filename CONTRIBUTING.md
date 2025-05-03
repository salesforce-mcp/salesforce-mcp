# Contributing Guidelines

## Commit Style

We welcome all contributions — whether it's bug fixes, improvements to the code structure, or adding new MCP functions. Your pull requests are greatly appreciated!

Please ensure your changes are submitted in a **new branch** following the naming convention:
 
- Use lowercase letters only.
- Separate words with hyphens (`-`).
- Keep the description concise and relevant.

## Commit Messages

We follow **semantic commit conventions**, using an emoji to indicate the type of change followed by a clear, concise message summarizing the intent.


### Commit message

We use semantics commits. In practice we use a emoji as the first character of the commit message with the whole intend of the commit. This are types we use:

| commit type   | commit symbol | description                                                          |
| ------------- | ------------- | -----------                                                          |
| chore         | 🔨            | A change that affects to the build system o non-code files           |
| deletions     | 🔥            | Removal of files or deprecated components                            |
| deploy        | 🚀            | Deployment-related changes                                           |
| documentation | 📝            | Updates to documentation                                             |
| experiment    | 🧪            | Experiments, test commits, or proof-of-concept work                  |
| feat          | ✨            | Introduction of new features                                         |
| fix           | 🐛            | Bug fixes or resolution of technical/functional issues               |
| idea          | 💡            | Placeholder commits for new ideas                                    |
| perf          | ⚡️            | Performance improvements                                             |
| refac         | 🧩            | Code refactoring to improve maintainability                          |
| style         | 🎨            | Changes that affect only the visual or code style (e.g., formatting) |
| test          | ✅            | Addition or updates to unit, integration, or other types of tests    |
| tweak         | 🔧            | Minor adjustments that don't qualify as a new feature                |

Use a short and concise commit message with the main intention of the change, starting with uppercase letter. If you need to explain more things you can use multiline messages in the commit body

### Writing Commit Messages

- Start the message with the appropriate emoji and type.
- Use a **short, descriptive title** beginning with an **uppercase letter**.
- If more context is needed, use the commit body to explain the change in detail.
- Keep messages professional — avoid inappropriate language.

#### Examples

**Short format:**
```
✨ Add new mcp function for ListViews creation
```

**Extended format:**
```
🐛 Fix connection problems

The existing implementation led to undefined behavior when the session expired.
This commit adds token renewal logic to address the problem.
```

Thank you for contributing and helping us make this project better!
