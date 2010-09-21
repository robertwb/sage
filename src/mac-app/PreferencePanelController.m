//
//  PreferencePanelController.m
//
//  Created by Ivan Andrus on 26/6/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import "PreferencePanelController.h"
#import "MyDocument.h"
#import "AppController.h"

@implementation PreferencePanelController


- (void)windowDidBecomeKey:(NSNotification *)aNotification{

    NSUserDefaults *defaults;
    defaults = [NSUserDefaults standardUserDefaults];
    NSString *terminalEmulator = [defaults stringForKey:@"TerminalEmulator"];

    // Disable Showing in the Dock on Tiger
    if ( [appController isTigerOrLess] ) {
        [showInDock setEnabled:NO];
    }

    // Set up Terminal Emulation

    // We start with the items bundled with the application and
    // overwrite with those the user has saved.  This way the user
    // gets any items added in later versions.
    // TODO: we may want a way to delete them, but then we would never
    // be able to delete default ones which might be confusing and
    // frustrating
    // TODO: ideally we would only save those that the user has added or changed.
    NSMutableDictionary *terminalEmulatorList =
    [[NSMutableDictionary dictionaryWithContentsOfFile:
                [[NSBundle mainBundle] pathForResource:@"Defaults" ofType:@"plist"]]
     objectForKey:@"TerminalEmulatorList"];

    NSDictionary *savedTermEmuList = [defaults dictionaryForKey:@"TerminalEmulatorList"];
    NSEnumerator *enumerator = [savedTermEmuList keyEnumerator];
    id key;
    // extra parens to suppress warning about using = instead of ==
    while( (key = [enumerator nextObject]) ) {
        [terminalEmulatorList setObject:[savedTermEmuList objectForKey:key] forKey:key];
    }
    // Save to defaults since that's how we look it up later
    [defaults setObject:terminalEmulatorList forKey:@"TerminalEmulatorList"];
    // NSLog(@"TerminalEmulatorList:%@",terminalEmulatorList);

    // Add terminal emulators to UI
    [TerminalEmulator removeAllItems];
    // This isn't a great sorting method, but it doesn't matter that much.  I just want xterm and xterm -- don't exit next to each other
    [TerminalEmulator addItemsWithObjectValues:[[terminalEmulatorList allKeys] sortedArrayUsingSelector:@selector(caseInsensitiveCompare:)]];
    [TerminalEmulator setStringValue:terminalEmulator];
    [TerminalApplescript setStringValue:[terminalEmulatorList objectForKey:terminalEmulator]];

    // Set up Default Arguments
    NSDictionary *defaultArgList = [defaults dictionaryForKey:@"DefaultArguments"];
    [SessionType removeAllItems];
    [SessionType addItemsWithObjectValues:[defaultArgList allKeys]];
}

- (IBAction)apply:(id)sender{
    NSUserDefaults *defaults;
    defaults = [NSUserDefaults standardUserDefaults];

    NSString *terminalEmulator = [TerminalEmulator stringValue];
    [defaults setObject:terminalEmulator forKey:@"TerminalEmulator"];

    NSDictionary *terminalEmulatorList = [defaults dictionaryForKey:@"TerminalEmulatorList"];
    NSMutableDictionary *newList = [[terminalEmulatorList mutableCopy] autorelease];
    [newList setObject:[TerminalApplescript stringValue] forKey:terminalEmulator];

    // NSLog(@"%@ is now %@", terminalEmulatorList, newList);
    [defaults setObject:newList forKey:@"TerminalEmulatorList"];

    NSString *sessionType = [SessionType stringValue];
    if ( [sessionType length] > 0 ) {

        [defaults setObject:terminalEmulator forKey:@"SessionType"];

        NSDictionary *DefaultArgList = [defaults dictionaryForKey:@"DefaultArguments"];
        NSMutableDictionary *newList = [[DefaultArgList mutableCopy] autorelease];
        [newList setObject:[DefaultArgs stringValue] forKey:sessionType];

        // NSLog(@"%@ is now %@", DefaultArgList, newList);
        [defaults setObject:newList forKey:@"DefaultArguments"];
    }
}

- (IBAction)resetTerminalApplescript:(id)sender{

    NSDictionary *defaultTerminalEmulatorList =
    [[NSDictionary dictionaryWithContentsOfFile:
      [[NSBundle mainBundle] pathForResource:@"Defaults" ofType:@"plist"]]
     objectForKey:@"TerminalEmulatorList"];

    NSString *script = [defaultTerminalEmulatorList objectForKey:[TerminalEmulator stringValue]];
    if ( script != nil ) {
        [TerminalApplescript setStringValue:script];
    }
}

// This actually ensures the data will be correct
// http://www.cocoabuilder.com/archive/cocoa/221619-detecting-when-nscombobox-text-changed-by-list.html
- (void)controlTextDidEndEditing:(NSNotification *)aNotification{
    [appController setupPaths];
    [self updateForComboBoxChanges];
}

// This provides snappier feedback if selecting using the mouse
- (void)comboBoxWillDismiss:(NSNotification *)notification{
    [self updateForComboBoxChanges];
}

-(void)updateForComboBoxChanges{
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];

    NSDictionary *terminalEmulatorList = [defaults dictionaryForKey:@"TerminalEmulatorList"];
    NSString *terminalApplscript = [terminalEmulatorList objectForKey:[TerminalEmulator stringValue]];
    if ( terminalApplscript != nil ) {
        [TerminalApplescript setStringValue:[terminalEmulatorList objectForKey:[TerminalEmulator stringValue]]];
    }

    if ([[SessionType stringValue] length] > 0 ) {
        NSDictionary *defaultArgList = [defaults dictionaryForKey:@"DefaultArguments"];
        NSString *defArgstring = [defaultArgList objectForKey:[SessionType stringValue]];
        if ( defArgstring != nil ) {
            [DefaultArgs setStringValue:defArgstring];
        }
    }
}

@end
