---
title: "Swift in Doom Emacs"
author: "Yousuf Ali"
date: "2026-11-13"
categories: [swift, emacs]
format: html
---


# Swift Development in Doom Emacs on macOS

A practical guide to getting a full Swift/iOS development environment inside Doom Emacs.

---

## Prerequisites

- macOS with Xcode installed
- Doom Emacs configured
- `xcode-select --install` already run

---

## Step 1: Point Emacs at Your Xcode Toolchain

```lisp
(let* ((dev   (string-trim (shell-command-to-string "xcode-select -p")))
       (sklsp (expand-file-name
               "Toolchains/XcodeDefault.xctoolchain/usr/bin/sourcekit-lsp" dev)))
  (setenv "DEVELOPER_DIR" dev)
  (setq lsp-sourcekit-executable sklsp
        lsp-sourcekit-extra-args  nil))
```

**Why this works:**  
`xcode-select -p` returns the active developer directory (e.g. `/Applications/Xcode.app/Contents/Developer`). We dynamically derive the path to `sourcekit-lsp` from it rather than hardcoding, so it survives Xcode updates. Setting `DEVELOPER_DIR` in the environment ensures child processes (builds, LSP server) also know where the toolchain lives.

---

## Step 2: Configure Tree-sitter Parser Path

```lisp
(setq lsp-ts-query-parser-install-directories
      ["/YOUR_HOME/.config/emacs/.local/cache/tree-sitter"])
```

Replace `/YOUR_HOME` with your home directory path, or use `(expand-file-name "~/.config/emacs/.local/cache/tree-sitter")`.

**Why this works:**  
Doom caches tree-sitter grammars here. Telling `lsp-mode` where they live enables richer semantic highlighting and navigation.

---

## Step 3: Install the Local Swift Packages

clone from here [github](https://github.com/konrad1977/swift-development) in localpackages directory. 

```
~/.config/doom/
└── localpackages/
    └── swift-development/
        ├── swift-development.el
        ├── xcode-project.el
        ├── xcode-build-config.el
        ├── ios-simulator.el
        ├── swift-refactor.el
        └── localizeable-mode.el
```

Then load them in your `config.el`:

```lisp
(require 'transient)

(add-to-list 'load-path
             (expand-file-name "localpackages/swift-development" doom-private-dir))

(require 'swift-development)
(require 'xcode-project)
(require 'xcode-build-config)
(require 'ios-simulator)
(require 'swift-refactor)
(require 'localizeable-mode)
```

**Why this works:**  
`doom-private-dir` points to your Doom config directory. Adding the subfolder to `load-path` lets Emacs find the `.el` files with `require`. `transient` is loaded first because the Swift modules use it for menu-driven commands (like Magit-style popups).

---

## Step 4: Bind Local Leader Keys for Swift

```lisp
(map! :after (swift-mode swift-ts-mode)
      :map (swift-mode-map swift-ts-mode-map)
      :localleader
      "b" #'swift-development-compile-and-run
      "B" #'swift-development-compile-app
      "r" #'swift-development-run
      "i" #'swift-incremental-build-compile-and-run
      "t" #'swift-test-explorer-toggle
      "p" #'swiftui-preview-toggle)
```

**Why this works:**  
`:after` defers binding until the mode is loaded, avoiding errors at startup. `:localleader` maps to `,` in Doom by default, so inside any Swift file you get:

| Key | Action |
|-----|--------|
| `, b` | Compile and run |
| `, B` | Compile only |
| `, r` | Run |
| `, i` | Incremental build + run |
| `, t` | Toggle test explorer |
| `, p` | Toggle SwiftUI preview |

---

## Step 5: Fix the Compiler Environment Leak

This is an easy-to-miss but important step:

```lisp
(setq process-environment
      (cl-remove-if
       (lambda (env)
         (string-match-p
          "^\\(LIBRARY_PATH\\|CPATH\\|C_INCLUDE_PATH\\|OBJC_INCLUDE_PATH\\)=" env))
       process-environment))
```

**Why this works:**  
When Emacs is compiled with native compilation (`libgccjit`), it injects `LIBRARY_PATH`, `CPATH`, and related variables into its own environment. These leak into every subprocess — including Xcode builds and the Swift compiler — causing confusing linker errors like:

```
ld: warning: ignoring file ... unexpected architecture
```

Filtering them out before any build process runs keeps Xcode's environment clean.

---

## Step 6: Send Region to Swift REPL

```lisp
(map! :after swift-mode
      :map swift-mode-map
      :n [C-return] #'swift-mode:send-region)
```

**Why this works:**  
In normal mode, `C-RET` sends the selected region to the Swift REPL. Great for quick experimentation without a full build cycle.

---

## Final `config.el` (Assembled)

```lisp
;;; --- Xcode Toolchain + SourceKit-LSP ---
(let* ((dev   (string-trim (shell-command-to-string "xcode-select -p")))
       (sklsp (expand-file-name
               "Toolchains/XcodeDefault.xctoolchain/usr/bin/sourcekit-lsp" dev)))
  (setenv "DEVELOPER_DIR" dev)
  (setq lsp-sourcekit-executable sklsp
        lsp-sourcekit-extra-args  nil))

;;; --- Tree-sitter Parser Cache ---
(setq lsp-ts-query-parser-install-directories
      ["/YOUR_HOME/.config/emacs/.local/cache/tree-sitter"])

;;; --- Fix Compiler Environment Leak ---
(setq process-environment
      (cl-remove-if
       (lambda (env)
         (string-match-p
          "^\\(LIBRARY_PATH\\|CPATH\\|C_INCLUDE_PATH\\|OBJC_INCLUDE_PATH\\)=" env))
       process-environment))

;;; --- Swift Development Packages ---
(require 'transient)
(add-to-list 'load-path
             (expand-file-name "localpackages/swift-development" doom-private-dir))

(require 'swift-development)
(require 'xcode-project)
(require 'xcode-build-config)
(require 'ios-simulator)
(require 'swift-refactor)
(require 'localizeable-mode)

;;; --- Keybindings ---
(map! :after (swift-mode swift-ts-mode)
      :map (swift-mode-map swift-ts-mode-map)
      :localleader
      "b" #'swift-development-compile-and-run
      "B" #'swift-development-compile-app
      "r" #'swift-development-run
      "i" #'swift-incremental-build-compile-and-run
      "t" #'swift-test-explorer-toggle
      "p" #'swiftui-preview-toggle)

(map! :after swift-mode
      :map swift-mode-map
      :n [C-return] #'swift-mode:send-region)
```

---

## Enabling in `packages.el`

Make sure these are in your `packages.el`:

```lisp
(package! swift-mode)
(package! lsp-sourcekit)
```

Then run `doom sync` and restart Emacs.

---

That's it. Open any `.swift` file and LSP should start automatically, your local leader keys will be available, and your builds won't be polluted by Emacs's internal compiler paths.
